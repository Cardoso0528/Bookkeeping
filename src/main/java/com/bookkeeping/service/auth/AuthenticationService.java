package com.bookkeeping.service.auth;

import com.bookkeeping.domain.entity.RefreshToken;
import com.bookkeeping.domain.entity.Tenant;
import com.bookkeeping.domain.entity.User;
import com.bookkeeping.domain.enums.AuthProvider;
import com.bookkeeping.domain.enums.BusinessType;
import com.bookkeeping.domain.enums.UserRole;
import com.bookkeeping.dto.auth.*;
import com.bookkeeping.repository.RefreshTokenRepository;
import com.bookkeeping.repository.TenantRepository;
import com.bookkeeping.repository.UserRepository;
import com.bookkeeping.security.context.TenantContext;
import com.bookkeeping.security.jwt.JwtService;
import com.google.api.client.googleapis.auth.oauth2.GoogleIdToken;
import com.google.api.client.googleapis.auth.oauth2.GoogleIdTokenVerifier;
import com.google.api.client.http.javanet.NetHttpTransport;
import com.google.api.client.json.gson.GsonFactory;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.Collections;
import java.util.Optional;

/**
 * Core authentication service handling registration, login, OAuth, and token management.
 *
 * Security measures:
 * - Passwords hashed with BCrypt (strength 12)
 * - Google ID tokens verified server-side (signature, audience, expiry)
 * - Refresh tokens stored as SHA-256 hashes
 * - Token rotation on refresh (old token revoked)
 * - Generic error messages to prevent account enumeration
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class AuthenticationService {

    private final UserRepository userRepository;
    private final TenantRepository tenantRepository;
    private final RefreshTokenRepository refreshTokenRepository;
    private final JwtService jwtService;
    private final PasswordEncoder passwordEncoder;
    private final AuthenticationManager authenticationManager;

    @Value("${google.client-id:}")
    private String googleClientId;

    /**
     * Register a new user with email/password.
     * Creates a new Tenant and User (as OWNER).
     */
    @Transactional
    public AuthResponse register(RegisterRequest request) {
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new BadCredentialsException("Registration failed. Please try again.");
        }

        BusinessType businessType;
        try {
            businessType = BusinessType.valueOf(request.getBusinessType().toUpperCase());
        } catch (IllegalArgumentException e) {
            throw new IllegalArgumentException("Invalid business type: " + request.getBusinessType());
        }

        Tenant tenant = Tenant.builder()
                .businessName(request.getBusinessName())
                .businessType(businessType)
                .build();
        tenant = tenantRepository.save(tenant);

        TenantContext.setCurrentTenantId(tenant.getId());
        try {
            User user = User.builder()
                    .email(request.getEmail())
                    .passwordHash(passwordEncoder.encode(request.getPassword()))
                    .role(UserRole.OWNER)
                    .firstName(request.getFirstName())
                    .lastName(request.getLastName())
                    .authProvider(AuthProvider.LOCAL)
                    .build();
            user = userRepository.save(user);

            log.info("New user registered: {} (tenant: {})", user.getEmail(), tenant.getId());
            return buildAuthResponse(user);
        } finally {
            TenantContext.clear();
        }
    }

    /**
     * Authenticate a user with email/password.
     * Uses Spring Security's AuthenticationManager for constant-time comparison.
     */
    @Transactional
    public AuthResponse login(LoginRequest request) {
        authenticationManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                        request.getEmail(),
                        request.getPassword()
                )
        );

        User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new BadCredentialsException("Invalid credentials"));

        if (!user.getIsActive()) {
            throw new BadCredentialsException("Invalid credentials");
        }

        log.info("User logged in: {}", user.getEmail());
        return buildAuthResponse(user);
    }

    /**
     * Authenticate via Google OAuth2.
     * Verifies the Google ID token server-side, then creates or retrieves the user.
     *
     * Security: Never trusts client-provided email/name. All info is extracted
     * from the verified Google ID token.
     */
    @Transactional
    public AuthResponse authenticateGoogle(GoogleOAuthRequest request) {
        GoogleIdToken idToken = verifyGoogleToken(request.getIdToken());
        if (idToken == null) {
            throw new BadCredentialsException("Invalid Google credentials");
        }

        GoogleIdToken.Payload payload = idToken.getPayload();
        String googleSubjectId = payload.getSubject();
        String email = payload.getEmail();
        Boolean emailVerified = payload.getEmailVerified();
        String firstName = (String) payload.get("given_name");
        String lastName = (String) payload.get("family_name");

        if (email == null || !Boolean.TRUE.equals(emailVerified)) {
            throw new BadCredentialsException("Google account email not verified");
        }

        Optional<User> existingOAuthUser = userRepository.findByAuthProviderAndProviderId(
                AuthProvider.GOOGLE, googleSubjectId
        );

        if (existingOAuthUser.isPresent()) {
            User user = existingOAuthUser.get();
            if (!user.getIsActive()) {
                throw new BadCredentialsException("Invalid credentials");
            }
            log.info("Google OAuth login: {}", user.getEmail());
            return buildAuthResponse(user);
        }

        Optional<User> existingEmailUser = userRepository.findByEmail(email);
        if (existingEmailUser.isPresent()) {
            User user = existingEmailUser.get();
            user.setAuthProvider(AuthProvider.GOOGLE);
            user.setProviderId(googleSubjectId);
            user = userRepository.save(user);
            log.info("Linked Google account to existing user: {}", user.getEmail());
            return buildAuthResponse(user);
        }

        Tenant tenant = Tenant.builder()
                .businessName(email.split("@")[0] + "'s Business")
                .businessType(BusinessType.OTHER)
                .build();
        tenant = tenantRepository.save(tenant);

        TenantContext.setCurrentTenantId(tenant.getId());
        try {
            User user = User.builder()
                    .email(email)
                    .role(UserRole.OWNER)
                    .firstName(firstName)
                    .lastName(lastName)
                    .authProvider(AuthProvider.GOOGLE)
                    .providerId(googleSubjectId)
                    .build();
            user = userRepository.save(user);

            log.info("New Google OAuth user registered: {} (tenant: {})", user.getEmail(), tenant.getId());
            return buildAuthResponse(user);
        } finally {
            TenantContext.clear();
        }
    }

    /**
     * Refresh an access token using a valid refresh token.
     * Implements token rotation: the old refresh token is revoked and a new one is issued.
     */
    @Transactional
    public AuthResponse refreshToken(RefreshTokenRequest request) {
        String tokenHash = jwtService.hashToken(request.getRefreshToken());
        RefreshToken storedToken = refreshTokenRepository.findByTokenHash(tokenHash)
                .orElseThrow(() -> new BadCredentialsException("Invalid refresh token"));

        if (!storedToken.isUsable()) {
            refreshTokenRepository.revokeAllByUserId(storedToken.getUserId());
            throw new BadCredentialsException("Refresh token expired or revoked");
        }

        storedToken.setRevoked(true);
        refreshTokenRepository.save(storedToken);

        User user = userRepository.findById(storedToken.getUserId())
                .orElseThrow(() -> new BadCredentialsException("Invalid refresh token"));

        if (!user.getIsActive()) {
            throw new BadCredentialsException("Invalid refresh token");
        }

        log.debug("Token refreshed for user: {}", user.getEmail());
        return buildAuthResponse(user);
    }

    /**
     * Revoke a refresh token (logout).
     */
    @Transactional
    public void logout(RefreshTokenRequest request) {
        String tokenHash = jwtService.hashToken(request.getRefreshToken());
        refreshTokenRepository.findByTokenHash(tokenHash).ifPresent(token -> {
            token.setRevoked(true);
            refreshTokenRepository.save(token);
            log.info("Refresh token revoked for user: {}", token.getUserId());
        });
    }

    /**
     * Build the authentication response with access + refresh tokens.
     */
    private AuthResponse buildAuthResponse(User user) {
        String accessToken = jwtService.generateAccessToken(user);
        String rawRefreshToken = jwtService.generateRefreshToken();
        String refreshTokenHash = jwtService.hashToken(rawRefreshToken);

        RefreshToken refreshTokenEntity = RefreshToken.builder()
                .userId(user.getId())
                .tokenHash(refreshTokenHash)
                .expiresAt(Instant.now().plusMillis(jwtService.getRefreshTokenExpiration()))
                .build();
        refreshTokenRepository.save(refreshTokenEntity);

        UserResponse userResponse = UserResponse.builder()
                .id(user.getId())
                .email(user.getEmail())
                .firstName(user.getFirstName())
                .lastName(user.getLastName())
                .role(user.getRole().name())
                .authProvider(user.getAuthProvider().name())
                .build();

        return AuthResponse.builder()
                .accessToken(accessToken)
                .refreshToken(rawRefreshToken)
                .expiresIn(jwtService.getAccessTokenExpiration() / 1000)
                .tokenType("Bearer")
                .user(userResponse)
                .build();
    }

    /**
     * Verify Google ID token server-side.
     * Checks: signature validity, audience matches our client ID, token not expired.
     */
    private GoogleIdToken verifyGoogleToken(String idTokenString) {
        try {
            GoogleIdTokenVerifier verifier = new GoogleIdTokenVerifier.Builder(
                    new NetHttpTransport(),
                    GsonFactory.getDefaultInstance()
            )
                    .setAudience(Collections.singletonList(googleClientId))
                    .build();

            return verifier.verify(idTokenString);
        } catch (Exception e) {
            log.warn("Google ID token verification failed: {}", e.getMessage());
            return null;
        }
    }
}

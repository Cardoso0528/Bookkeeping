package com.bookkeeping.controller;

import com.bookkeeping.dto.auth.*;
import com.bookkeeping.service.auth.AuthenticationService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

/**
 * REST controller for authentication endpoints.
 * All endpoints are publicly accessible (/api/auth/** is permitted in SecurityConfig).
 */
@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
@Slf4j
public class AuthController {

    private final AuthenticationService authenticationService;

    /**
     * Register a new user with email/password.
     * Creates a new tenant and user (as OWNER).
     */
    @PostMapping("/register")
    public ResponseEntity<AuthResponse> register(
            @Valid @RequestBody RegisterRequest request
    ) {
        log.debug("Registration request for email: {}", request.getEmail());
        AuthResponse response = authenticationService.register(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    /**
     * Authenticate with email/password.
     */
    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(
            @Valid @RequestBody LoginRequest request
    ) {
        log.debug("Login request for email: {}", request.getEmail());
        AuthResponse response = authenticationService.login(request);
        return ResponseEntity.ok(response);
    }

    /**
     * Authenticate via Google OAuth2.
     * Frontend sends the Google ID token obtained from Google Sign-In.
     */
    @PostMapping("/oauth2/google")
    public ResponseEntity<AuthResponse> googleOAuth(
            @Valid @RequestBody GoogleOAuthRequest request
    ) {
        log.debug("Google OAuth request received");
        AuthResponse response = authenticationService.authenticateGoogle(request);
        return ResponseEntity.ok(response);
    }

    /**
     * Refresh an access token using a valid refresh token.
     * Implements token rotation (old refresh token is revoked).
     */
    @PostMapping("/refresh")
    public ResponseEntity<AuthResponse> refreshToken(
            @Valid @RequestBody RefreshTokenRequest request
    ) {
        log.debug("Token refresh request received");
        AuthResponse response = authenticationService.refreshToken(request);
        return ResponseEntity.ok(response);
    }

    /**
     * Revoke a refresh token (logout).
     */
    @PostMapping("/logout")
    public ResponseEntity<Void> logout(
            @Valid @RequestBody RefreshTokenRequest request
    ) {
        log.debug("Logout request received");
        authenticationService.logout(request);
        return ResponseEntity.noContent().build();
    }
}

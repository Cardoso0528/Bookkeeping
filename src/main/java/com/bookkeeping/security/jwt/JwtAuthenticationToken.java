package com.bookkeeping.security.jwt;

import lombok.Getter;
import org.springframework.security.authentication.AbstractAuthenticationToken;
import org.springframework.security.core.GrantedAuthority;

import java.util.Collection;
import java.util.UUID;

/**
 * Custom authentication token that carries JWT-extracted user identity.
 * Stores userId, email, tenantId, and role for downstream use.
 */
@Getter
public class JwtAuthenticationToken extends AbstractAuthenticationToken {

    private final UUID userId;
    private final String email;
    private final UUID tenantId;
    private final String role;

    public JwtAuthenticationToken(
            UUID userId,
            String email,
            UUID tenantId,
            String role,
            Collection<? extends GrantedAuthority> authorities
    ) {
        super(authorities);
        this.userId = userId;
        this.email = email;
        this.tenantId = tenantId;
        this.role = role;
        setAuthenticated(true);
    }

    @Override
    public Object getCredentials() {
        return null;
    }

    @Override
    public Object getPrincipal() {
        return userId;
    }
}

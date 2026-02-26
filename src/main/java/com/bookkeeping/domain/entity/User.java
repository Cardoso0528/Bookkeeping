package com.bookkeeping.domain.entity;

import com.bookkeeping.domain.enums.AuthProvider;
import com.bookkeeping.domain.enums.UserRole;
import jakarta.persistence.*;
import lombok.*;

/**
 * User entity representing application users.
 * Each user belongs to a tenant and has a specific role.
 * Supports both email/password (LOCAL) and OAuth (GOOGLE) authentication.
 */
@Entity
@Table(
    name = "users",
    uniqueConstraints = {
        @UniqueConstraint(columnNames = {"tenant_id", "email"})
    },
    indexes = {
        @Index(name = "idx_users_tenant", columnList = "tenant_id"),
        @Index(name = "idx_users_email", columnList = "email"),
        @Index(name = "idx_users_auth_provider", columnList = "auth_provider")
    }
)
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User extends TenantAwareEntity {

    @Column(name = "email", nullable = false, length = 255)
    private String email;

    @Column(name = "password_hash", length = 255)
    private String passwordHash;

    @Enumerated(EnumType.STRING)
    @Column(name = "auth_provider", nullable = false, length = 20)
    @Builder.Default
    private AuthProvider authProvider = AuthProvider.LOCAL;

    @Column(name = "provider_id", length = 255)
    private String providerId;

    @Enumerated(EnumType.STRING)
    @Column(name = "role", nullable = false, length = 20)
    private UserRole role;

    @Column(name = "first_name", length = 100)
    private String firstName;

    @Column(name = "last_name", length = 100)
    private String lastName;

    @Column(name = "is_active")
    @Builder.Default
    private Boolean isActive = true;

    /**
     * Get full name of the user.
     */
    public String getFullName() {
        if (firstName != null && lastName != null) {
            return firstName + " " + lastName;
        } else if (firstName != null) {
            return firstName;
        } else if (lastName != null) {
            return lastName;
        }
        return email;
    }
}

package com.bookkeeping.repository;

import com.bookkeeping.domain.entity.User;
import com.bookkeeping.domain.enums.AuthProvider;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Repository for User entities.
 */
@Repository
public interface UserRepository extends JpaRepository<User, UUID> {

    /**
     * Find user by email and tenant ID.
     *
     * @param email Email address
     * @param tenantId Tenant ID
     * @return Optional containing user if found
     */
    Optional<User> findByEmailAndTenantId(String email, UUID tenantId);

    /**
     * Find user by email (unique across all tenants).
     *
     * @param email Email address
     * @return Optional containing user if found
     */
    Optional<User> findByEmail(String email);

    /**
     * Find all users for a specific tenant.
     *
     * @param tenantId Tenant ID
     * @return List of users
     */
    List<User> findByTenantId(UUID tenantId);

    /**
     * Check if a user exists with the given email and tenant.
     *
     * @param email Email address
     * @param tenantId Tenant ID
     * @return true if exists
     */
    boolean existsByEmailAndTenantId(String email, UUID tenantId);

    /**
     * Check if a user exists with the given email.
     *
     * @param email Email address
     * @return true if exists
     */
    boolean existsByEmail(String email);

    /**
     * Find user by OAuth provider and provider-specific ID.
     *
     * @param authProvider The auth provider (GOOGLE, etc.)
     * @param providerId The provider-specific user ID
     * @return Optional containing user if found
     */
    Optional<User> findByAuthProviderAndProviderId(AuthProvider authProvider, String providerId);
}

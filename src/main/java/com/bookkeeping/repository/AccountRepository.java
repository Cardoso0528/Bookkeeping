package com.bookkeeping.repository;

import com.bookkeeping.domain.entity.Account;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Repository for Account entities.
 */
@Repository
public interface AccountRepository extends JpaRepository<Account, UUID> {

    /**
     * Find all accounts for a specific tenant.
     *
     * @param tenantId Tenant ID
     * @return List of accounts
     */
    List<Account> findByTenantId(UUID tenantId);

    /**
     * Find all active accounts for a tenant.
     *
     * @param tenantId Tenant ID
     * @param isActive Active status
     * @return List of active accounts
     */
    List<Account> findByTenantIdAndIsActive(UUID tenantId, Boolean isActive);

    /**
     * Find account by ID and tenant ID (for security).
     *
     * @param id Account ID
     * @param tenantId Tenant ID
     * @return Optional containing account if found
     */
    Optional<Account> findByIdAndTenantId(UUID id, UUID tenantId);
}

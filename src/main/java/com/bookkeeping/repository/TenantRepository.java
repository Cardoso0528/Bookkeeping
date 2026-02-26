package com.bookkeeping.repository;

import com.bookkeeping.domain.entity.Tenant;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;
import java.util.UUID;

/**
 * Repository for Tenant entities.
 */
@Repository
public interface TenantRepository extends JpaRepository<Tenant, UUID> {

    /**
     * Find tenant by business name.
     *
     * @param businessName Business name to search for
     * @return Optional containing tenant if found
     */
    Optional<Tenant> findByBusinessName(String businessName);

    /**
     * Check if a tenant exists with the given business name.
     *
     * @param businessName Business name to check
     * @return true if exists
     */
    boolean existsByBusinessName(String businessName);
}

package com.bookkeeping.repository;

import com.bookkeeping.domain.entity.Category;
import com.bookkeeping.domain.enums.BusinessType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Repository for Category entities.
 */
@Repository
public interface CategoryRepository extends JpaRepository<Category, UUID> {

    /**
     * Find all categories for a tenant.
     *
     * @param tenantId Tenant ID
     * @return List of categories
     */
    List<Category> findByTenantId(UUID tenantId);

    /**
     * Find categories for a specific business type.
     *
     * @param tenantId Tenant ID
     * @param businessType Business type
     * @return List of categories
     */
    List<Category> findByTenantIdAndBusinessType(UUID tenantId, BusinessType businessType);

    /**
     * Find categories applicable to a business type (including generic ones).
     * Returns both business-specific categories AND generic categories (where businessType is NULL).
     *
     * @param tenantId Tenant ID
     * @param businessType Business type
     * @return List of applicable categories
     */
    @Query("SELECT c FROM Category c WHERE c.tenantId = :tenantId " +
           "AND (c.businessType = :businessType OR c.businessType IS NULL)")
    List<Category> findApplicableCategories(
        @Param("tenantId") UUID tenantId,
        @Param("businessType") BusinessType businessType
    );

    /**
     * Find system default categories.
     *
     * @param tenantId Tenant ID
     * @return List of system categories
     */
    List<Category> findByTenantIdAndIsSystemDefaultTrue(UUID tenantId);

    /**
     * Find tax-deductible categories.
     *
     * @param tenantId Tenant ID
     * @return List of tax-deductible categories
     */
    List<Category> findByTenantIdAndIsTaxDeductibleTrue(UUID tenantId);

    /**
     * Find category by name and tenant.
     *
     * @param categoryName Category name
     * @param tenantId Tenant ID
     * @return Optional containing category if found
     */
    Optional<Category> findByCategoryNameAndTenantId(String categoryName, UUID tenantId);

    /**
     * Find category by ID and tenant ID (for security).
     *
     * @param id Category ID
     * @param tenantId Tenant ID
     * @return Optional containing category if found
     */
    Optional<Category> findByIdAndTenantId(UUID id, UUID tenantId);

    /**
     * Check if a category name exists for a tenant.
     *
     * @param categoryName Category name
     * @param tenantId Tenant ID
     * @return true if exists
     */
    boolean existsByCategoryNameAndTenantId(String categoryName, UUID tenantId);
}

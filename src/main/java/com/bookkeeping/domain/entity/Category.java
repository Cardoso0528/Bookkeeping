package com.bookkeeping.domain.entity;

import com.bookkeeping.domain.enums.BusinessType;
import jakarta.persistence.*;
import lombok.*;

import java.util.UUID;

/**
 * Category entity for transaction categorization.
 *
 * Categories can be:
 * - System defaults (applicable to all business types)
 * - Business-type-specific (e.g., "Food Costs" for restaurants)
 * - Custom (user-created for their specific needs)
 */
@Entity
@Table(
    name = "categories",
    indexes = {
        @Index(name = "idx_categories_tenant", columnList = "tenant_id"),
        @Index(name = "idx_categories_business_type", columnList = "business_type")
    }
)
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Category extends TenantAwareEntity {

    @Column(name = "category_name", nullable = false, length = 100)
    private String categoryName;

    /**
     * Business type this category applies to.
     * NULL = applies to all business types (default categories)
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "business_type", length = 50)
    private BusinessType businessType;

    /**
     * Parent category for hierarchical categorization.
     * Example: "Meals & Entertainment" > "Client Meals"
     */
    @Column(name = "parent_category_id")
    private UUID parentCategoryId;

    /**
     * True if this is a system-provided default category.
     * System categories cannot be deleted by users.
     */
    @Column(name = "is_system_default")
    @Builder.Default
    private Boolean isSystemDefault = false;

    /**
     * True if expenses in this category are typically tax-deductible.
     */
    @Column(name = "is_tax_deductible")
    @Builder.Default
    private Boolean isTaxDeductible = false;

    @Column(name = "description", length = 500)
    private String description;

    /**
     * Check if this category is specific to a business type.
     */
    public boolean isBusinessSpecific() {
        return businessType != null;
    }

    /**
     * Check if this category has a parent.
     */
    public boolean hasParent() {
        return parentCategoryId != null;
    }
}

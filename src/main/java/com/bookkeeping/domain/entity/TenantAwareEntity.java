package com.bookkeeping.domain.entity;

import com.bookkeeping.security.context.TenantContext;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import java.time.Instant;
import java.util.UUID;

/**
 * Base entity class for all multi-tenant entities.
 * Automatically sets tenant_id from ThreadLocal context on persist.
 *
 * CRITICAL: All entities that extend this class will automatically
 * have tenant_id set before persisting to the database.
 */
@MappedSuperclass
@Getter
@Setter
@EntityListeners(AuditingEntityListener.class)
public abstract class TenantAwareEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    /**
     * Tenant ID for multi-tenant data isolation.
     * Set automatically from TenantContext before persist.
     */
    @Column(name = "tenant_id", nullable = false, updatable = false)
    private UUID tenantId;

    @CreatedDate
    @Column(name = "created_at", nullable = false, updatable = false)
    private Instant createdAt;

    @LastModifiedDate
    @Column(name = "updated_at")
    private Instant updatedAt;

    /**
     * Called before persisting entity.
     * Automatically sets tenant_id from current tenant context.
     */
    @PrePersist
    public void prePersist() {
        if (tenantId == null) {
            tenantId = TenantContext.getCurrentTenantId();
            if (tenantId == null) {
                throw new IllegalStateException(
                    "Cannot persist entity without tenant context. " +
                    "Ensure TenantContext.setCurrentTenantId() is called."
                );
            }
        }
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof TenantAwareEntity)) return false;
        TenantAwareEntity that = (TenantAwareEntity) o;
        return id != null && id.equals(that.id);
    }

    @Override
    public int hashCode() {
        return getClass().hashCode();
    }
}

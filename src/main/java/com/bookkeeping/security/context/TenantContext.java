package com.bookkeeping.security.context;

import lombok.extern.slf4j.Slf4j;

import java.util.UUID;

/**
 * ThreadLocal-based tenant context for multi-tenancy.
 *
 * CRITICAL: This class stores the current tenant ID in ThreadLocal storage,
 * allowing each HTTP request to operate in its own tenant context.
 *
 * The TenantFilter sets this at the beginning of each request based on
 * the JWT token, and TenantAwareEntity reads from it when persisting entities.
 *
 * Usage:
 * - TenantFilter: Sets tenant ID from JWT
 * - TenantAwareEntity: Reads tenant ID when saving
 * - Services: Can read current tenant for queries
 *
 * IMPORTANT: Always clear() in a finally block to prevent memory leaks!
 */
@Slf4j
public class TenantContext {

    private static final ThreadLocal<UUID> currentTenant = new ThreadLocal<>();

    /**
     * Set the current tenant ID for this thread.
     *
     * @param tenantId The tenant ID to set
     */
    public static void setCurrentTenantId(UUID tenantId) {
        if (tenantId == null) {
            log.warn("Attempting to set null tenant ID");
            return;
        }
        log.debug("Setting tenant context: {}", tenantId);
        currentTenant.set(tenantId);
    }

    /**
     * Get the current tenant ID for this thread.
     *
     * @return Current tenant ID, or null if not set
     */
    public static UUID getCurrentTenantId() {
        UUID tenantId = currentTenant.get();
        if (tenantId == null) {
            log.warn("No tenant context found in current thread");
        }
        return tenantId;
    }

    /**
     * Clear the tenant context for this thread.
     *
     * CRITICAL: Must be called in finally block to prevent memory leaks
     * in thread pool environments.
     */
    public static void clear() {
        UUID tenantId = currentTenant.get();
        if (tenantId != null) {
            log.debug("Clearing tenant context: {}", tenantId);
        }
        currentTenant.remove();
    }

    /**
     * Check if tenant context is set for current thread.
     *
     * @return true if tenant context exists
     */
    public static boolean hasTenantContext() {
        return currentTenant.get() != null;
    }
}

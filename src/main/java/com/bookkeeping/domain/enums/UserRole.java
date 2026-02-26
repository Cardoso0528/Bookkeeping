package com.bookkeeping.domain.enums;

/**
 * User roles for role-based access control (RBAC).
 *
 * OWNER: Full access - can manage everything
 * ACCOUNTANT: Can manage financial data but not settings
 * VIEWER: Read-only access to reports and transactions
 */
public enum UserRole {
    OWNER("Owner", "Full access to all features"),
    ACCOUNTANT("Accountant", "Can manage financial data"),
    VIEWER("Viewer", "Read-only access");

    private final String displayName;
    private final String description;

    UserRole(String displayName, String description) {
        this.displayName = displayName;
        this.description = description;
    }

    public String getDisplayName() {
        return displayName;
    }

    public String getDescription() {
        return description;
    }
}

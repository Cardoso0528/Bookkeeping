package com.bookkeeping.domain.enums;

/**
 * Transaction types for double-entry bookkeeping.
 *
 * DEBIT: Money out (expenses, withdrawals)
 * CREDIT: Money in (revenue, deposits)
 *
 * For balance calculations:
 * - DEBIT transactions reduce account balance (negative)
 * - CREDIT transactions increase account balance (positive)
 */
public enum TransactionType {
    DEBIT("Debit", "Money out / Expense"),
    CREDIT("Credit", "Money in / Revenue");

    private final String displayName;
    private final String description;

    TransactionType(String displayName, String description) {
        this.displayName = displayName;
        this.description = description;
    }

    public String getDisplayName() {
        return displayName;
    }

    public String getDescription() {
        return description;
    }

    /**
     * Check if this transaction type increases balance.
     */
    public boolean increasesBalance() {
        return this == CREDIT;
    }

    /**
     * Check if this transaction type decreases balance.
     */
    public boolean decreasesBalance() {
        return this == DEBIT;
    }
}

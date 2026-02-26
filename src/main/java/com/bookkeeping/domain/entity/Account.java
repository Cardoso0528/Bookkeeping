package com.bookkeeping.domain.entity;

import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;

/**
 * Account entity representing bank accounts, credit cards, etc.
 *
 * CRITICAL: Uses BigDecimal for balance - NEVER use double/float for money!
 */
@Entity
@Table(
    name = "accounts",
    indexes = {
        @Index(name = "idx_accounts_tenant", columnList = "tenant_id")
    }
)
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Account extends TenantAwareEntity {

    @Column(name = "account_name", nullable = false, length = 255)
    private String accountName;

    @Column(name = "account_type", nullable = false, length = 50)
    private String accountType;  // CHECKING, SAVINGS, CREDIT_CARD

    /**
     * Account balance in the specified currency.
     *
     * CRITICAL: precision=19, scale=4 ensures accurate financial calculations.
     * - precision=19: total digits (supports up to $999 quadrillion)
     * - scale=4: decimal places (supports cents: 0.0001)
     */
    @Column(name = "balance", nullable = false, precision = 19, scale = 4)
    @Builder.Default
    private BigDecimal balance = BigDecimal.ZERO;

    @Column(name = "currency", length = 3)
    @Builder.Default
    private String currency = "USD";

    @Column(name = "is_active")
    @Builder.Default
    private Boolean isActive = true;

    @Column(name = "description", length = 500)
    private String description;

    /**
     * Update balance by adding the specified amount.
     *
     * @param amount Amount to add (can be negative for deductions)
     */
    public void updateBalance(BigDecimal amount) {
        if (amount == null) {
            throw new IllegalArgumentException("Amount cannot be null");
        }
        this.balance = this.balance.add(amount);
    }

    /**
     * Check if account has sufficient balance.
     *
     * @param amount Amount to check
     * @return true if balance >= amount
     */
    public boolean hasSufficientBalance(BigDecimal amount) {
        return balance.compareTo(amount) >= 0;
    }
}

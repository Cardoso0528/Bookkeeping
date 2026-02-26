package com.bookkeeping.domain.entity;

import com.bookkeeping.domain.enums.TransactionType;
import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.UUID;

/**
 * Transaction entity representing financial transactions.
 *
 * CRITICAL IMPLEMENTATION NOTES:
 * 1. Uses BigDecimal for amounts - NEVER use double/float for money
 * 2. precision=19, scale=4 in database (DECIMAL(19,4))
 * 3. All amount comparisons must use .compareTo(), NOT ==
 * 4. Division operations must specify rounding mode
 */
@Entity
@Table(
    name = "transactions",
    indexes = {
        @Index(name = "idx_transactions_tenant_date", columnList = "tenant_id,transaction_date DESC"),
        @Index(name = "idx_transactions_account", columnList = "account_id"),
        @Index(name = "idx_transactions_category", columnList = "category_id")
    }
)
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Transaction extends TenantAwareEntity {

    /**
     * Account this transaction belongs to.
     */
    @Column(name = "account_id", nullable = false)
    private UUID accountId;

    /**
     * Date of the transaction (not timestamp - we don't care about time).
     */
    @Column(name = "transaction_date", nullable = false)
    private LocalDate transactionDate;

    /**
     * Transaction amount (always positive).
     * Use TransactionType to determine if it's debit or credit.
     *
     * CRITICAL: precision=19, scale=4
     * - Supports up to $999,999,999,999,999.9999
     * - 4 decimal places for accuracy
     */
    @Column(name = "amount", nullable = false, precision = 19, scale = 4)
    private BigDecimal amount;

    /**
     * Transaction type: DEBIT (expense) or CREDIT (revenue).
     */
    @Enumerated(EnumType.STRING)
    @Column(name = "transaction_type", nullable = false, length = 20)
    private TransactionType transactionType;

    /**
     * Category this transaction is assigned to.
     */
    @Column(name = "category_id")
    private UUID categoryId;

    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    @Column(name = "merchant_name", length = 255)
    private String merchantName;

    /**
     * Whether this transaction is tax-deductible.
     * Can be set manually or suggested by AI.
     */
    @Column(name = "is_tax_deductible")
    @Builder.Default
    private Boolean isTaxDeductible = false;

    /**
     * AI categorization confidence score (0.00 to 1.00).
     * NULL if manually categorized.
     */
    @Column(name = "confidence_score", precision = 3, scale = 2)
    private BigDecimal confidenceScore;

    /**
     * Source of the transaction data.
     * Values: MANUAL, BANK_IMPORT, OCR
     */
    @Column(name = "source", length = 50)
    private String source;

    @Column(name = "notes", columnDefinition = "TEXT")
    private String notes;

    /**
     * Get the signed amount for balance calculations.
     * DEBIT: negative (money out)
     * CREDIT: positive (money in)
     *
     * @return Signed amount
     */
    public BigDecimal getSignedAmount() {
        if (amount == null) {
            return BigDecimal.ZERO;
        }
        return transactionType == TransactionType.DEBIT
            ? amount.negate()
            : amount;
    }

    /**
     * Check if this transaction is categorized.
     */
    public boolean isCategorized() {
        return categoryId != null;
    }

    /**
     * Check if this transaction was AI-categorized.
     */
    public boolean isAiCategorized() {
        return confidenceScore != null;
    }

    /**
     * Check if this is an expense (debit).
     */
    public boolean isExpense() {
        return transactionType == TransactionType.DEBIT;
    }

    /**
     * Check if this is revenue (credit).
     */
    public boolean isRevenue() {
        return transactionType == TransactionType.CREDIT;
    }
}

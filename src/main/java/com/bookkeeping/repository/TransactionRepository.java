package com.bookkeeping.repository;

import com.bookkeeping.domain.entity.Transaction;
import com.bookkeeping.domain.enums.TransactionType;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * Repository for Transaction entities.
 */
@Repository
public interface TransactionRepository extends JpaRepository<Transaction, UUID> {

    /**
     * Find all transactions for a tenant with pagination.
     *
     * @param tenantId Tenant ID
     * @param pageable Pagination parameters
     * @return Page of transactions
     */
    Page<Transaction> findByTenantId(UUID tenantId, Pageable pageable);

    /**
     * Find transactions for an account ordered by date.
     *
     * @param accountId Account ID
     * @return List of transactions
     */
    List<Transaction> findByAccountIdOrderByTransactionDateAsc(UUID accountId);

    /**
     * Find transactions for a tenant within a date range.
     *
     * @param tenantId Tenant ID
     * @param startDate Start date (inclusive)
     * @param endDate End date (inclusive)
     * @return List of transactions
     */
    List<Transaction> findByTenantIdAndTransactionDateBetween(
        UUID tenantId,
        LocalDate startDate,
        LocalDate endDate
    );

    /**
     * Find uncategorized transactions for a tenant.
     *
     * @param tenantId Tenant ID
     * @return List of uncategorized transactions
     */
    List<Transaction> findByTenantIdAndCategoryIdIsNull(UUID tenantId);

    /**
     * Find transactions by category.
     *
     * @param categoryId Category ID
     * @return List of transactions
     */
    List<Transaction> findByCategoryId(UUID categoryId);

    /**
     * Find transactions by type within date range.
     *
     * @param tenantId Tenant ID
     * @param transactionType Transaction type (DEBIT/CREDIT)
     * @param startDate Start date
     * @param endDate End date
     * @return List of transactions
     */
    List<Transaction> findByTenantIdAndTransactionTypeAndTransactionDateBetween(
        UUID tenantId,
        TransactionType transactionType,
        LocalDate startDate,
        LocalDate endDate
    );

    /**
     * Check if duplicate transaction exists (for CSV import deduplication).
     *
     * @param accountId Account ID
     * @param transactionDate Transaction date
     * @param amount Amount
     * @param description Description
     * @return true if duplicate exists
     */
    boolean existsByAccountIdAndTransactionDateAndAmountAndDescription(
        UUID accountId,
        LocalDate transactionDate,
        java.math.BigDecimal amount,
        String description
    );

    /**
     * Find transaction by ID and tenant ID (for security).
     *
     * @param id Transaction ID
     * @param tenantId Tenant ID
     * @return Optional containing transaction if found
     */
    Optional<Transaction> findByIdAndTenantId(UUID id, UUID tenantId);

    /**
     * Count uncategorized transactions for a tenant.
     *
     * @param tenantId Tenant ID
     * @return Count of uncategorized transactions
     */
    long countByTenantIdAndCategoryIdIsNull(UUID tenantId);
}

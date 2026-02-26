package com.bookkeeping;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Main Spring Boot application class for AI-Powered Bookkeeping Application.
 *
 * This application provides:
 * - Multi-tenant bookkeeping for small businesses
 * - AI-powered transaction categorization
 * - Document OCR (receipts, invoices)
 * - Financial reporting (P&L, cash flow forecasting)
 * - Tax deduction suggestions
 *
 * Architecture:
 * - Spring Boot 3.2.1 + Java 17
 * - PostgreSQL for data persistence
 * - JWT authentication
 * - Multi-tenant isolation via TenantContext
 *
 * @author AI Bookkeeping Team
 */
@SpringBootApplication
public class BookkeepingApplication {

    public static void main(String[] args) {
        SpringApplication.run(BookkeepingApplication.class, args);
    }
}

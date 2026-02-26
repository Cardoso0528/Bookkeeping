package com.bookkeeping.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;

/**
 * JPA configuration for the application.
 *
 * Enables JPA Auditing for automatic management of:
 * - @CreatedDate
 * - @LastModifiedDate
 * - @CreatedBy
 * - @LastModifiedBy
 */
@Configuration
@EnableJpaAuditing
public class JpaConfig {
    // JPA Auditing is now enabled
}

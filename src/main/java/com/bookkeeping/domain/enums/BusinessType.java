package com.bookkeeping.domain.enums;

import lombok.Getter;

/**
 * Types of businesses supported by the application.
 * Each business type has different expense categories and tax rules.
 */
@Getter
public enum BusinessType {
    RESTAURANT("Restaurant", "Food service, bars, cafes"),
    CONSULTING("Consulting", "Professional services, advisors"),
    RETAIL("Retail", "Stores, e-commerce"),
    CONTRACTING("Contracting", "Construction, contractors"),
    FREELANCE("Freelance", "Independent contractors, gig workers"),
    OTHER("Other", "Other business types");

    private final String displayName;
    private final String description;

    BusinessType(String displayName, String description) {
        this.displayName = displayName;
        this.description = description;
    }

}

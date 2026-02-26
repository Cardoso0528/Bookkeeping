package com.bookkeeping.domain.enums;

/**
 * Processing status for documents (receipts, invoices, bank statements).
 * Used to track OCR and data extraction progress.
 */
public enum ProcessingStatus {
    PENDING("Pending", "Waiting to be processed"),
    PROCESSING("Processing", "Currently being processed"),
    COMPLETED("Completed", "Successfully processed"),
    FAILED("Failed", "Processing failed");

    private final String displayName;
    private final String description;

    ProcessingStatus(String displayName, String description) {
        this.displayName = displayName;
        this.description = description;
    }

    public String getDisplayName() {
        return displayName;
    }

    public String getDescription() {
        return description;
    }

    public boolean isComplete() {
        return this == COMPLETED;
    }

    public boolean isFailed() {
        return this == FAILED;
    }

    public boolean isPending() {
        return this == PENDING || this == PROCESSING;
    }
}

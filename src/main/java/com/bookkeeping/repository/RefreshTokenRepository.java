package com.bookkeeping.repository;

import com.bookkeeping.domain.entity.RefreshToken;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.time.Instant;
import java.util.Optional;
import java.util.UUID;

/**
 * Repository for RefreshToken entities.
 */
@Repository
public interface RefreshTokenRepository extends JpaRepository<RefreshToken, UUID> {

    /**
     * Find a refresh token by its SHA-256 hash.
     *
     * @param tokenHash SHA-256 hash of the refresh token
     * @return Optional containing the token record if found
     */
    Optional<RefreshToken> findByTokenHash(String tokenHash);

    /**
     * Revoke all refresh tokens for a user (used for logout-all).
     *
     * @param userId User ID
     */
    @Modifying
    @Query("UPDATE RefreshToken rt SET rt.revoked = true WHERE rt.userId = :userId AND rt.revoked = false")
    void revokeAllByUserId(@Param("userId") UUID userId);

    /**
     * Delete all expired refresh tokens (housekeeping).
     *
     * @param now Current timestamp
     */
    @Modifying
    @Query("DELETE FROM RefreshToken rt WHERE rt.expiresAt < :now")
    void deleteExpiredTokens(@Param("now") Instant now);

    /**
     * Delete all tokens for a user (used on account deletion).
     *
     * @param userId User ID
     */
    void deleteByUserId(UUID userId);
}

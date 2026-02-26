package com.bookkeeping.dto.auth;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * DTO for Google OAuth2 authentication requests.
 * The client sends the Google ID token obtained from the Google Sign-In flow.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class GoogleOAuthRequest {

    @NotBlank(message = "Google ID token is required")
    private String idToken;
}

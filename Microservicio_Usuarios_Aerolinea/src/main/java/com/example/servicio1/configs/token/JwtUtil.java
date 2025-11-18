package com.example.servicio1.configs.token;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.SignatureAlgorithm;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import java.security.Key;
import java.util.Date;

@Component
public class JwtUtil {
    @Value("${jwt.secret:J9arT8avL4aqP2adW7ayB1azM6aeN0afS3agJ5ahK8auY2aR4aC7aA9aZ1aaD0axV6aT5aO3aP8aqE2amL9aF7asH5aK2aN4aR8aV3aY1apB0azC6aG9aX5atJ7aaL2adM4afN8awQ0aeS3arH1auT9aP5aoE7aZ2aiV6ayB3acA8aD4ajO9aL1akF0arT7apN5abM2agS4aeW3aqY6ahJ8anU0aR9aC5aV7aX4atB1aK3aG2aL8aoD6aaF9asM0awE7anH4afP1arS5auQ2aT3aiY8aZ0ajV6a}")
    private String SECRET_KEY;
    @Value("${jwt.expiration-ms:86400000}")
    private long EXPIRATION_MS;

    private Key getSigningKey() {
        return Keys.hmacShaKeyFor(SECRET_KEY.getBytes());
    }

    public String generateToken(Long id, String rol, String email) {
        return Jwts.builder()
                .claim("id", id)
                .claim("rol", rol)
                .claim("email", email)
                .setIssuedAt(new Date())
                .setExpiration(new Date(System.currentTimeMillis() + EXPIRATION_MS))
                .signWith(getSigningKey(), SignatureAlgorithm.HS256)
                .compact();
    }

    public Claims extractAllClaims(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(getSigningKey())
                .build()
                .parseClaimsJws(token)
                .getBody();
    }

    public boolean isTokenValid(String token) {
        try {
            Claims claims = extractAllClaims(token);
            return claims.getExpiration().after(new Date());
        } catch (Exception e) {
            return false;
        }
    }

    public String extractEmail(String token) {
        return extractAllClaims(token).get("email", String.class);
    }

    public String extractRol(String token) {
        return extractAllClaims(token).get("rol", String.class);
    }

    public Long extractId(String token) {
        return extractAllClaims(token).get("id", Long.class);
    }

    public long getExpirationMs() {
        return EXPIRATION_MS;
    }
}

package com.example.servicio1.configs.security;

import com.example.servicio1.configs.token.JwtUtil;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import java.io.IOException;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtUtil jwtUtil;
    private static final Logger log = LoggerFactory.getLogger(JwtAuthenticationFilter.class);

    public JwtAuthenticationFilter(JwtUtil jwtUtil) {
        this.jwtUtil = jwtUtil;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain) throws ServletException, IOException {
        String path = request.getRequestURI();
        String method = request.getMethod();
        log.info("Ruta entrante al filtro JWT: {} {}", method, path);

        // Si otro filtro (por ejemplo, ApiKeyAuthenticationFilter) ya autenticó la solicitud,
        // no intentamos validar JWT y dejamos continuar la cadena.
        if (SecurityContextHolder.getContext().getAuthentication() != null) {
            filterChain.doFilter(request, response);
            return;
        }

        // --- CORRECCIÓN ---
        // Lógica de exclusión simplificada para que coincida
        // exactamente con las reglas de SecurityConfig.
        
        log.info("🐛 DEBUG: Evaluando exclusión para ruta: {} {}", method, path);
        log.info("🐛 DEBUG: ¿Coincide con /Servicio1/api/usuarios/save/? ${}", path.matches("^/Servicio1/api/usuarios/save/?$"));
        
        // 1. Comprobar rutas estáticas (es más rápido) con tolerancia de barra final y variantes sin contexto
        if (path.matches("^/Servicio1/api/personas/login/?$") ||
            path.matches("^/Servicio1/api/usuarios/save/?$") ||
            path.matches("^/Servicio1/api/admins/save/?$") ||
            path.matches("^/api/personas/login/?$") ||
            path.matches("^/api/usuarios/save/?$") ||
            path.matches("^/api/admins/save/?$") ||
            // Swagger UI y OpenAPI
            path.matches("^/Servicio1/swagger-ui.html$") ||
            path.matches("^/Servicio1/v3/api-docs/?$")
        ) {
            log.info("✅ Exclusión 1 - Ruta pública estática: {} {}", method, path);
            filterChain.doFilter(request, response);
            return;
        }

        // 2. Comprobar rutas dinámicas (con Regex)
        // (Nota: path.matches() evalúa la cadena COMPLETA)
        if (path.matches("/Servicio1/api/personas/email/[^/]+") ||
            path.matches("/Servicio1/api/personas/update/\\d+") ||
            path.matches("/Servicio1/api/personas/updatePassword/\\d+") ||
            // Swagger UI y OpenAPI dinámicos
            path.matches("/Servicio1/swagger-ui/.*") ||
            path.matches("/Servicio1/v3/api-docs/.*")
        ) {
            log.info("✅ Exclusión 2 - Ruta pública dinámica: {} {}", method, path);
            filterChain.doFilter(request, response);
            return;
        }

        // Endpoints públicos de lectura (GET) para usuarios/admins/empleados/personas, excluyendo /me
        // IMPORTANTE: Solo aplica a métodos GET (lectura), no a POST/PUT/DELETE (escritura)
        if (request.getMethod().equals("GET") &&
            (path.matches("/Servicio1/api/usuarios/.*") ||
             path.matches("/Servicio1/api/admins/.*") ||
             path.matches("/Servicio1/api/empleados/.*") ||
             path.matches("/Servicio1/api/personas/.*")) &&
            !path.equals("/Servicio1/api/personas/me")) {
            log.info("✅ Exclusión 3 - Ruta pública GET: {} {}", method, path);
            filterChain.doFilter(request, response);
            return;
        }
        
        // --- FIN DE LA LÓGICA DE EXCLUSIÓN ---
        
        // Si llegamos aquí, ninguna exclusión aplicó - vamos a validar JWT
        log.info("🔄 Ninguna exclusión aplicó - validando JWT para: {} {}", method, path);
        
        // Buscar cookie JWT_TOKEN
        Cookie[] cookies = request.getCookies();
        String token = null;
        if (cookies != null) {
            for (Cookie cookie : cookies) {
                if ("JWT_TOKEN".equals(cookie.getName())) {
                    token = cookie.getValue();
                    break;
                }
            }
        }
        
        // Si no hay token o es inválido → 401
        if (token == null || !jwtUtil.isTokenValid(token)) {
            response.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Token inválido o no proporcionado");
            return;
        }
        
        // Si el token es válido → autenticar
        String email = jwtUtil.extractEmail(token);
        Object principal = (email != null && !email.isBlank()) ? email : jwtUtil.extractId(token);
        UsernamePasswordAuthenticationToken authToken =
                new UsernamePasswordAuthenticationToken(principal, null, List.of());
        authToken.setDetails(new WebAuthenticationDetailsSource().buildDetails(request));
        SecurityContextHolder.getContext().setAuthentication(authToken);
        filterChain.doFilter(request, response);
    }
}

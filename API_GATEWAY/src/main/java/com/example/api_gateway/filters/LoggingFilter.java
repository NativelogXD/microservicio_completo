package com.example.api_gateway.filters;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

@Component // Anotación de Spring que indica que esta clase es un bean manejado por el contenedor de Spring.
public class LoggingFilter implements GlobalFilter, Ordered {
    // La clase implementa GlobalFilter, lo que significa que actuará como un filtro global para todas las solicitudes
    // que pasen por el Spring Cloud Gateway.
    // También implementa Ordered, lo que permite definir el orden de ejecución de los filtros.

    private static final Logger log = LoggerFactory.getLogger(LoggingFilter.class);
    // Se crea un logger usando SLF4J para registrar información de logs sobre las solicitudes entrantes.

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        // Este método se ejecuta cada vez que llega una solicitud al Gateway.
        log.info(">>> Request Gateway: {} {}", exchange.getRequest().getMethod(), exchange.getRequest().getURI());
        // Registra en el log el método HTTP (GET, POST, etc.) y la URI de la solicitud entrante.

        return chain.filter(exchange);
        // Continúa la cadena de filtros para que la solicitud llegue al siguiente filtro o al servicio destino.
    }

    @Override
    public int getOrder() {
        return -1;
        // Define la prioridad del filtro. Un valor menor significa mayor prioridad.
        // Aquí se indica que este filtro debe ejecutarse antes que la mayoría de los otros filtros.
    }
}



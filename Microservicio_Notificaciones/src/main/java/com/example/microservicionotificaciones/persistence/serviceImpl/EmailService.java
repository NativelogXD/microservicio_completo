package com.example.microservicionotificaciones.persistence.serviceImpl;

import com.example.microservicionotificaciones.domain.dto.NotificacionDTO;
import com.sendgrid.*;
import com.sendgrid.helpers.mail.Mail;
import com.sendgrid.helpers.mail.objects.Email;
import com.sendgrid.helpers.mail.objects.Personalization;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import java.io.IOException;

@Slf4j
@Service("EMAIL")
public class EmailService {

    @Value("${sendgrid.api.key}")
    private String sendGridApiKey;

    @Value("${sendgrid.from.email}")
    private String fromEmail;


    public void enviarNotificacion(NotificacionDTO notificacion) {
        log.info("Enviando EMAIL a persona {}: {}", notificacion.getId_persona(), notificacion.getMensaje());

        Email from = new Email(fromEmail);
        Email to = new Email(notificacion.getEmailDestino());

        Mail mail = new Mail();
        mail.setFrom(from);
        // El asunto y el contenido serán definidos por la plantilla, por eso se omiten las líneas directas de subject y content

        Personalization personalization = new Personalization();
        personalization.addTo(to);

        // Configura el ID de la plantilla dinámica (Template ID)
        mail.setTemplateId("d-dca50750ba4d42a281a0d9fc353b3f33");

        // Añade los datos dinámicos que coinciden con las etiquetas de tu plantilla (ej: {{titulo}}, {{mensaje}})
        personalization.addDynamicTemplateData("titulo", notificacion.getTitulo());
        personalization.addDynamicTemplateData("mensaje", notificacion.getMensaje());

        mail.addPersonalization(personalization);

        SendGrid sg = new SendGrid(sendGridApiKey);
        Request request = new Request();

        try {
            request.setMethod(Method.POST);
            request.setEndpoint("mail/send");
            request.setBody(mail.build());

            Response response = sg.api(request);

            // Debería retornar un 202 Accepted si todo está correcto
            log.info("Respuesta de SendGrid - Status Code: {}", response.getStatusCode());
            log.debug("Body: {}", response.getBody());
            log.debug("Headers: {}", response.getHeaders());

        } catch (IOException e) {
            log.error("Error al enviar el correo con SendGrid", e);
        }
    }
}

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import EmailLog

def send_email(subject, template_html, template_txt, context, to):
    try:
        from_email = None
        html_content = render_to_string(template_html, context)
        text_content = render_to_string(template_txt, context)
        
        email = EmailMultiAlternatives(subject, text_content, from_email, [to])
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        EmailLog.objects.create(recipient=to, subject=subject, status="sent")
    except Exception as e:
        EmailLog.objects.create(recipient=to, subject=subject, status="failed")
        raise 
    
def send_welcome_email(user):
    context = {"user": user}
    send_email(
        "Bem-vindo ao nosso sistema!",
        "emails/welcome.html",
        "emails/welcome.html", 
        context,
        user.email
    )
    
def send_welcome_change_password_email(user, password, reset_link):
    context = {"user": user, "password": password, "reset_link": reset_link}
    send_email(
        "Bem-vindo ao nosso sistema! - Alteração de senha necessária",
        "emails/welcome_change_password.html",
        "emails/welcome_change_password.html", 
        context,
        user.email
    )
    
def send_reset_password_email(user, reset_link):
    context = {"user": user, "reset_link": reset_link}
    
    # send_email(
    #     "Redefinição de senha",
    #     "emails/reset_password.html",
    #     "emails/reset_password.html",
    #     context,
    #     user.email
    # )

def send_verification_email(user, verification_link):
    context = {"user": user, "verification_link": verification_link}
    send_email(
        "Verificação de e-mail",
        "emails/verify_email.html",
        "emails/verify_email.html",
        context,
        user.email
    )
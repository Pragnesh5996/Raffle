from .models import WinnderEmail, LoserEmail
from .Apis import Required_api
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings

# Send Winner Email #
def SendWinnerEmail(subscriber_email, product_id, variant_id, raffle_id, shop, token, url):
    content = ''
    product = Required_api.get_product_title(product_id=str(product_id), shop=shop, token=token)
    variant = Required_api.get_variant_title(variant_id=str(variant_id), shop=shop, token=token)
    # print(type(product), type(variant))
    email_subject = 'Raffle Lucky Draw on ' + product
    
    subject, from_email, to = email_subject, settings.EMAIL_HOST_USER, subscriber_email
    
    check_winner_email = WinnderEmail.objects.filter(Raffle_id_id=str(raffle_id))
    if check_winner_email:
        content = check_winner_email[0].winnertemplate
    else:
        content = ''

    message = render_to_string('WinnerEmail.html', {'url': url, 'Content':content % (product, variant, product)})
   
    mssg = EmailMessage(
        subject,
        message,
        from_email,
        [to],
    )
    mssg.content_subtype = "html"  # Main content is now text/html
    mssg.send(fail_silently=False,)
    msg = "Account successfully created"
    return msg

# Send Loser Email #
def SendLoserEmail(subscriber_email, product_id, variant_id, raffle_id, shop, token):
    content = ''
    product = Required_api.get_product_title(product_id=product_id, shop=shop, token=token)
    variant = Required_api.get_variant_title(variant_id=variant_id, shop=shop, token=token)

    email_subject = 'Raffle Lucky Draw on ' + product
    
    subject, from_email, to = email_subject, settings.EMAIL_HOST_USER, subscriber_email
    
    check_loser_email = LoserEmail.objects.filter(Raffle_id_id=str(raffle_id))
    if check_loser_email:
        content = check_loser_email[0].losertemplate
    else:
        content = ''

    message = render_to_string('LoserEmail.html', {'Content':content % (product, variant)})
   
    mssg = EmailMessage(
        subject,
        message,
        from_email,
        [to],
    )
    mssg.content_subtype = "html"  # Main content is now text/html
    mssg.send(fail_silently=False,)
    msg = "Account successfully created"
    return msg

def SendVendorEmail(url, vendor_email):
    email_subject = 'Please select raffle winner manually'

    subject, from_email, to = email_subject, settings.EMAIL_HOST_USER, vendor_email

    message = render_to_string('VendorEmail.html', {'url': url})

    mssg = EmailMessage(
        subject,
        message,
        from_email,
        [to],
    )
    mssg.content_subtype = "html"
    mssg.send(fail_silently=False,)
    msg = "Account successfully created"
    return msg
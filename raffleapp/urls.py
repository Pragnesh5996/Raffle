from django.urls import path
from . import views
from .webhook import WebhookApi as wb
from .customer_raffle import get_raffle_detail
# from .testing import check_send_winner_email
from .cronFinal import Select

urlpatterns = [

    # '''From Views.py'''
    path('', views.login, name='index'),                        # https://raffle.pagekite.me/login
    path('installation', views.installation),
    path('final', views.final),                                 # https://raffle.pagekite.me/final
    
    # Product Detail Link #
    path('product', views.product),                             # https://raffle.pagekite.me/product

    # Raffle Form Link #
    path('raffle', views.raffle),                               # https://raffle.pagekite.me/raffle

    # Raffle List Link #
    path('upcoming_raffle', views.upcoming_raffle),             # https://raffle.pagekite.me/upcoming_raffle

    # New Raffle Link  #
    path('new_raffle', views.new_raffle),                       # https://raffle.pagekite.me/new_raffle
    path('get_new_raffle_detail', views.get_new_raffle_detail), # https://raffle.pagekite.me/get_new_raffle_detail
    path('subscribers', views.subscribers),                     # https://raffle.pagekite.me/subscribers

    # Old Raffle Link #
    path('old_raffle', views.old_raffle),                       # https://raffle.pagekite.me/old_raffle
    path('get_old_raffle_detail', views.get_old_raffle_detail), # https://raffle.pagekite.me/get_old_raffle_detail
    path('old_subscribers', views.old_subscribers),             # https://raffle.pagekite.me/old_subscribers

    # Dashboard Link #
    path('dashboard', views.dashboard),                         # https://raffle.pagekite.me/dashboard

    # Common Link for New/Old Raffle #
    path('delete_subscriber', views.delete_subscriber),         # https://raffle.pagekite.me/delete_subscriber
    # path('customer_redirect', views.customer_redirect),       # https://raffle.pagekite.me/customer_redirect

    # Create Ongoing Winner/Loser Email Link #
    path('WinnerEmailTemplate', views.WinnerEmailTemplate),     # https://raffle.pagekite.me/WinnerEmailTemplate
    path('LoserEmailTemplate', views.LoserEmailTemplate),       # https://raffle.pagekite.me/LoserEmailTemplate

    # Create Upcoming Winner/Loser Email Link #
    path('UpcomingWinnerEmail', views.UpcomingWinnerEmail),     # https://raffle.pagekite.me/UpcomingWinnerEmail
    path('UpcomingLoserEmail', views.UpcomingLoserEmail),       # https://raffle.pagekite.me/UpcomingLoserEmail

    # '''webhook.py'''
    path('uninstall', wb.webhook_uninstall),                    # https://raffle.pagekite.me/uninstall

    #'''FrontEnd Create Customer Link'''#
    path('create_customer', views.create_customer),             # https://raffle.pagekite.me/create_customer

    #'''FrontEnd Check Raffle Link'''#
    path('check_raffle_activation', views.check_raffle_activation), # https://raffle.pagekite.me/check_raffle_activation

    #'''FrontEnd Get Raffle Detail Link'''
    path('get_raffle_detail', get_raffle_detail),               # https://raffle.pagekite.me/get_raffle_detail
    path('SelectWinnerManually', views.SelectWinnerManually),    # https://raffle.pagekite.me/SelectWinnerManually

    path('Select', Select),
]
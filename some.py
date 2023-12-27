payment_link = Payment.objects.get(pk=payment_id)
        payment_id = payment_link.paid_payment_id

        transfer_url = (
            "https://api.razorpay.com/v1/payments/" + payment_id + "/transfers"
        )

        transfer_data = {"transfers": transfer_list}

        transfer_response = requests.post(
            transfer_url,
            auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET),
            headers={"Contact-Type": "application/json"},
            json=transfer_data,
        )
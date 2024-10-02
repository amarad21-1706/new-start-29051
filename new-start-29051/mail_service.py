
import requests

def send_simple_message222():
	return requests.post(
		"https://api.eu.mailgun.net/v3/sandbox8fe87aee4b91456c9d17ffcb802d8b20.mailgun.org/messages",
		auth=("api", "20cb76ced830ab536fa7cd718d1c1141-b02bcf9f-5936b742"),
		data={"from": "Mailgun Sandbox <postmaster@sandbox8fe87aee4b91456c9d17ffcb802d8b20.mailgun.org>",
			"to": "Astridel RADULESCU <amarad21@gmail.com>",
			"subject": "Hello Astridel RADULESCU",
			"text": "Congratulations Astridel RADULESCU, you just sent an email with Mailgun! You are truly awesome!"})

# You can see a record of this email in your logs: https://app.mailgun.com/app/logs.

# You can send up to 300 emails/day from this sandbox server.
# Next, you should add your own domain so you can send 10000 emails/month for free.


import logging

def send_simple_message(api_key, domain, sender, recipient, subject, text):
  """
  Sends a simple email using the Mailgun API.

  Args:
      api_key (str): Your Mailgun API key.
      domain (str): Your Mailgun domain name.
      sender (str): Email address of the sender.
      recipient (str): Email address of the recipient.
      subject (str): Subject line of the email.
      text (str): Body content of the email (in plain text).

  Returns:
      None
  """

  logger = logging.getLogger(__name__)

  url = f"https://api.eu.mailgun.net/v3/{domain}/messages"

  params = {
      "from": sender,
      "to": recipient,
      "subject": subject,
      "text": text
  }

  headers = {
      "Authorization": f"Basic {api_key}"
  }

  try:
      response = requests.post(url, params=params, headers=headers)
      response.raise_for_status()  # Raise an exception for non-200 status codes
      logger.info("Email sent successfully")
  except requests.exceptions.RequestException as e:
      logger.error(f"Failed to send email: {e}")


def send_simple_message333():
	return requests.post(
		"https://api.mailgun.net/v3/sandbox87b2fe045d8a47c18fbe5cea0163ee17.mailgun.org/messages",
		auth=("api", "<PRIVATE_API_KEY>"),
		data={"from": "Mailgun Sandbox <postmaster@sandbox87b2fe045d8a47c18fbe5cea0163ee17.mailgun.org>",
			"to": "Astridel RADULESCU <a24r09@gmail.com>",
			"subject": "Hello Astridel RADULESCU",
			"text": "Congratulations Astridel RADULESCU, you just sent an email with Mailgun! You are truly awesome!"})

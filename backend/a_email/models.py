from django.db import models

class EmailLog(models.Model):
    recipient = models.EmailField()
    subject = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default="sent") 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} → {self.recipient} ({self.status})"
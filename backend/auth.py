import smtplib
import random
from datetime import datetime
from email.mime.text import MIMEText
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------- Database Setup ----------------
Base = declarative_base()
engine = create_engine("sqlite:///users.db", echo=False)
Session = sessionmaker(bind=engine)

# ---------------- Models ----------------
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    phone = Column(String, nullable=True)             # ✅ new field
    profile_image = Column(String, nullable=True)     # ✅ new field
    otp = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)

    documents = relationship("Document", back_populates="user")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="documents")

# Create all tables
Base.metadata.create_all(engine)

# ---------------- Email Config ----------------
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "sakshijadhao1@gmail.com"
EMAIL_PASSWORD = "eydj pups pdic trur"   # ⚠️ use App Password for Gmail

def send_email(to_email, subject, body):
    """Helper to send email using SMTP"""
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print("Email error:", e)
        return False

# ---------------- Auth Functions ----------------
def register_user(username, email, password):
    """Register new user or resend OTP if already exists but not verified."""
    session = Session()
    user = session.query(User).filter_by(email=email).first()

    if user:
        if user.is_verified:
            session.close()
            return False, "Email already registered and verified!"
        else:
            # Resend OTP
            otp = str(random.randint(100000, 999999))
            user.otp = otp
            session.commit()
            session.close()
            if send_email(email, "Verify your account", f"Your OTP is {otp}"):
                return True, "Account exists but not verified. OTP resent!"
            else:
                return False, "Failed to send OTP. Check email config."
    else:
        # Create new user
        hashed_password = generate_password_hash(password)
        otp = str(random.randint(100000, 999999))
        new_user = User(username=username, email=email, password=hashed_password, otp=otp)
        session.add(new_user)
        session.commit()
        session.close()
        if send_email(email, "Verify your account", f"Your OTP is {otp}"):
            return True, "Registered successfully! OTP sent to your email."
        else:
            return False, "Failed to send OTP. Check email config."

def verify_otp(email, otp):
    """Verify user account with OTP."""
    session = Session()
    user = session.query(User).filter_by(email=email).first()
    if user and user.otp == otp:
        user.is_verified = True
        user.otp = None
        session.commit()
        session.close()
        return True, "✅ Account verified successfully!"
    else:
        session.close()
        return False, "❌ Invalid OTP!"

def login_user(email, password):
    """Login only if user exists, password matches, and is verified."""
    session = Session()
    user = session.query(User).filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        if user.is_verified:
            session.expunge(user)  # detach user so session can close safely
            session.close()
            return user   # return User object
        else:
            session.close()
            return None  # not verified
    session.close()
    return None

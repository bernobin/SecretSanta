from typing import Optional
import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKeyConstraint, Identity, PrimaryKeyConstraint, Text, UniqueConstraint, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        PrimaryKeyConstraint('userid', name='users_pkey'),
        UniqueConstraint('chatid', name='users_chatid_key')
    )

    userid: Mapped[int] = mapped_column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, autoincrement=True)
    chatid: Mapped[int] = mapped_column(BigInteger, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(Text)
    first_name: Mapped[Optional[str]] = mapped_column(Text)
    last_name: Mapped[Optional[str]] = mapped_column(Text)

    sessions: Mapped[list['Sessions']] = relationship('Sessions', back_populates='users')
    participant: Mapped[list['Participant']] = relationship('Participant', back_populates='user')


class Sessions(Base):
    __tablename__ = 'sessions'
    __table_args__ = (
        ForeignKeyConstraint(['admin_userid'], ['users.userid'], name='sessions_admin_userid_fkey'),
        PrimaryKeyConstraint('sessionid', name='sessions_pkey'),
        UniqueConstraint('sessionname', name='sessions_sessionname_key')
    )

    sessionid: Mapped[int] = mapped_column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, autoincrement=True)
    sessionname: Mapped[str] = mapped_column(Text, nullable=False)
    admin_userid: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'new'::text"))
    seed: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))
    ended_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(True))

    users: Mapped['Users'] = relationship('Users', back_populates='sessions')
    participant: Mapped[list['Participant']] = relationship('Participant', back_populates='session')


class Participant(Base):
    __tablename__ = 'participant'
    __table_args__ = (
        ForeignKeyConstraint(['session_id'], ['sessions.sessionid'], ondelete='CASCADE', name='participant_session_id_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.userid'], ondelete='CASCADE', name='participant_user_id_fkey'),
        PrimaryKeyConstraint('participant_id', name='participant_pkey'),
        UniqueConstraint('participant_id', 'session_id', name='participant_id_session_key'),
        UniqueConstraint('user_id', 'session_id', name='participant_user_session_key')
    )

    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    session_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    signed_up_at: Mapped[datetime.datetime] = mapped_column(DateTime(True), nullable=False, server_default=text('now()'))
    emoji: Mapped[str] = mapped_column(Text, nullable=False)
    participant_id: Mapped[int] = mapped_column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, autoincrement=True)

    session: Mapped['Sessions'] = relationship('Sessions', back_populates='participant')
    user: Mapped['Users'] = relationship('Users', back_populates='participant')
    gift_assignment_giver_participant_giver_session: Mapped['GiftAssignment'] = relationship('GiftAssignment', uselist=False, foreign_keys='[GiftAssignment.giver_participant_id, GiftAssignment.giver_session_id]', back_populates='participant_giver_participant_giver_session')
    gift_assignment_recipient_participant_recipient_session: Mapped['GiftAssignment'] = relationship('GiftAssignment', uselist=False, foreign_keys='[GiftAssignment.recipient_participant_id, GiftAssignment.recipient_session_id]', back_populates='participant_recipient_participant_recipient_session')


class GiftAssignment(Base):
    __tablename__ = 'gift_assignment'
    __table_args__ = (
        CheckConstraint('giver_participant_id <> recipient_participant_id', name='gift_assignment_no_self_gifting'),
        CheckConstraint('giver_session_id = recipient_session_id', name='gift_assignment_same_session'),
        ForeignKeyConstraint(['giver_participant_id', 'giver_session_id'], ['participant.participant_id', 'participant.session_id'], ondelete='CASCADE', name='gift_assignment_giver_participant_id_giver_session_id_fkey'),
        ForeignKeyConstraint(['recipient_participant_id', 'recipient_session_id'], ['participant.participant_id', 'participant.session_id'], ondelete='CASCADE', name='gift_assignment_recipient_participant_id_recipient_session_fkey'),
        PrimaryKeyConstraint('assignment_id', name='gift_assignment_pkey'),
        UniqueConstraint('giver_session_id', 'giver_participant_id', name='gift_assignment_one_gift_per_giver'),
        UniqueConstraint('recipient_session_id', 'recipient_participant_id', name='gift_assignment_recipient_session_id_recipient_participant_id')
    )

    assignment_id: Mapped[int] = mapped_column(BigInteger, Identity(always=True, start=1, increment=1, minvalue=1, maxvalue=9223372036854775807, cycle=False, cache=1), primary_key=True, autoincrement=True)
    giver_session_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    giver_participant_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    recipient_participant_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    recipient_session_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    participant_giver_participant_giver_session: Mapped['Participant'] = relationship('Participant', foreign_keys=[giver_participant_id, giver_session_id], back_populates='gift_assignment_giver_participant_giver_session')
    participant_recipient_participant_recipient_session: Mapped['Participant'] = relationship('Participant', foreign_keys=[recipient_participant_id, recipient_session_id], back_populates='gift_assignment_recipient_participant_recipient_session')

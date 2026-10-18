-- Adminer 6.1.1 PostgreSQL 17.11 dump

CREATE TABLE "public"."gift_assignment" (
    "assignment_id" bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
    "giver_session_id" bigint NOT NULL,
    "giver_participant_id" bigint NOT NULL,
    "recipient_participant_id" bigint NOT NULL,
    "recipient_session_id" bigint NOT NULL,
    CONSTRAINT "gift_assignment_pkey" PRIMARY KEY ("assignment_id"),
    CONSTRAINT "gift_assignment_no_self_gifting" CHECK ((giver_participant_id <> recipient_participant_id)),
    CONSTRAINT "gift_assignment_same_session" CHECK ((giver_session_id = recipient_session_id))
);

CREATE UNIQUE INDEX gift_assignment_one_gift_per_giver ON "public"."gift_assignment" USING btree (giver_session_id, giver_participant_id);

CREATE UNIQUE INDEX gift_assignment_recipient_session_id_recipient_participant_id ON "public"."gift_assignment" USING btree (recipient_session_id, recipient_participant_id);


CREATE TABLE "public"."participant" (
    "user_id" bigint NOT NULL,
    "session_id" bigint NOT NULL,
    "signed_up_at" timestamptz DEFAULT now() NOT NULL,
    "emoji" text NOT NULL,
    "participant_id" bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
    CONSTRAINT "participant_pkey" PRIMARY KEY ("participant_id")
);

CREATE UNIQUE INDEX participant_user_session_key ON "public"."participant" USING btree (user_id, session_id);

CREATE UNIQUE INDEX participant_id_session_key ON "public"."participant" USING btree (participant_id, session_id);


CREATE TABLE "public"."sessions" (
    "sessionid" bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
    "sessionname" text NOT NULL,
    "admin_userid" bigint NOT NULL,
    "seed" text,
    "status" text DEFAULT 'new' NOT NULL,
    "started_at" timestamptz,
    "ended_at" timestamptz,
    CONSTRAINT "sessions_pkey" PRIMARY KEY ("sessionid")
);

CREATE UNIQUE INDEX sessions_sessionname_key ON "public"."sessions" USING btree (sessionname);


CREATE TABLE "public"."users" (
    "userid" bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
    "chatid" bigint NOT NULL,
    "username" text,
    "first_name" text,
    "last_name" text,
    CONSTRAINT "users_pkey" PRIMARY KEY ("userid")
);

CREATE UNIQUE INDEX users_chatid_key ON "public"."users" USING btree (chatid);


ALTER TABLE ONLY "public"."gift_assignment" ADD CONSTRAINT "gift_assignment_giver_participant_id_giver_session_id_fkey" FOREIGN KEY (giver_participant_id, giver_session_id) REFERENCES "public"."participant"(participant_id, session_id) ON DELETE CASCADE;
ALTER TABLE ONLY "public"."gift_assignment" ADD CONSTRAINT "gift_assignment_recipient_participant_id_recipient_session_fkey" FOREIGN KEY (recipient_participant_id, recipient_session_id) REFERENCES "public"."participant"(participant_id, session_id) ON DELETE CASCADE;

ALTER TABLE ONLY "public"."participant" ADD CONSTRAINT "participant_session_id_fkey" FOREIGN KEY (session_id) REFERENCES "public"."sessions"(sessionid) ON DELETE CASCADE;
ALTER TABLE ONLY "public"."participant" ADD CONSTRAINT "participant_user_id_fkey" FOREIGN KEY (user_id) REFERENCES "public"."users"(userid) ON DELETE CASCADE;

ALTER TABLE ONLY "public"."sessions" ADD CONSTRAINT "sessions_admin_userid_fkey" FOREIGN KEY (admin_userid) REFERENCES "public"."users"(userid);

-- 2026-10-18 10:15:55 UTC

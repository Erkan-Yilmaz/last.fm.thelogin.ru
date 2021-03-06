# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, unicode_literals

from datetime import datetime
from flask.ext.login import UserMixin
import json

from last_fm.db import db

__all__ = [b"User", b"Scrobble", b"UserArtist",
           b"ReleaseFeed", b"Release", b"UserRelease", b"UserArtistIgnore",
           b"ApproximateTrackLength", b"Coincidence",
           b"GuestVisit",
           b"Repeat", b"MilestoneCalculationTimestamp"]


class User(db.Model, UserMixin):
    id                          = db.Column(db.Integer, primary_key=True)    
    username                    = db.Column(db.String(32), unique=True)
    session_key                 = db.Column(db.String(32))
    data                        = db.Column(db.PickleType(pickler=json))
    data_updated                = db.Column(db.DateTime)

    devices                     = db.Column(db.PickleType(pickler=json), default=list)
    auto_add_devices            = db.Column(db.Boolean, default=True)

    registration                = db.Column(db.DateTime, default=datetime.now, nullable=True)
    last_visit                  = db.Column(db.DateTime, nullable=True)
    last_library_update         = db.Column(db.DateTime, nullable=True)

    download_scrobbles          = db.Column(db.Boolean, index=True, default=False)
    build_releases              = db.Column(db.Boolean, index=True, default=True)
    cheater                     = db.Column(db.Boolean, index=True, default=False)

    twitter_username            = db.Column(db.String(32))
    twitter_data                = db.Column(db.PickleType(pickler=json))
    twitter_data_updated        = db.Column(db.DateTime)
    twitter_oauth_token         = db.Column(db.String(64))
    twitter_oauth_token_secret  = db.Column(db.String(64))
    use_twitter_data            = db.Column(db.Boolean, default=False)

    twitter_track_repeats       = db.Column(db.Boolean, default=False)
    twitter_repeats_min_count   = db.Column(db.Integer, default=5)
    twitter_post_repeat_start   = db.Column(db.Boolean, default=True)

    twitter_track_artist_milestones = db.Column(db.Boolean, default=False)

    twitter_win_artist_races        = db.Column(db.Boolean, default=False)
    twitter_artist_races_min_count  = db.Column(db.Integer, default=250)
    twitter_lose_artist_races       = db.Column(db.Boolean, default=True)


class Scrobble(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("user.id"))
    artist          = db.Column(db.String(255), index=True)
    album           = db.Column(db.String(255), index=True)
    track           = db.Column(db.String(255), index=True)
    uts             = db.Column(db.Integer, index=True)

    u_ar            = db.Index(user_id, artist)
    u_ar_u          = db.Index(user_id, artist, uts)

    @property
    def datetime(self):
        return datetime.fromtimestamp(self.uts)

    @property
    def name(self):
        return " ".join([self.artist, "—", self.track])

    @property
    def track_length(self):
        if self.approximate_track_length:
            return self.approximate_track_length.length
        else:
            return None

    user                        = db.relationship("User", foreign_keys=[user_id])
    approximate_track_length    = db.relationship("ApproximateTrackLength", primaryjoin="(ApproximateTrackLength.artist == Scrobble.artist) & (ApproximateTrackLength.track == Scrobble.track)",
                                                                            foreign_keys=[artist, track])


class UserArtist(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("user.id"))
    artist      = db.Column(db.String(255), index=True)
    scrobbles   = db.Column(db.Integer, index=True)

    user        = db.relationship("User", foreign_keys=[user_id])

###


class ReleaseFeed(db.Model):
    id  = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255))


class Release(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    feed_id = db.Column(db.Integer, db.ForeignKey("release_feed.id"))
    url     = db.Column(db.String(255))
    date    = db.Column(db.DateTime)
    title   = db.Column(db.String(255), index=True)
    content = db.Column(db.Text)

    feed    = db.relationship("ReleaseFeed", foreign_keys=[feed_id])


class UserRelease(db.Model):
    id                  = db.Column(db.Integer, primary_key=True)
    user_id             = db.Column(db.Integer, db.ForeignKey("user.id"))
    release_id          = db.Column(db.Integer, db.ForeignKey("release.id"))
    artist              = db.Column(db.String(255))
    artist_scrobbles    = db.Column(db.Integer)

    user                = db.relationship("User", foreign_keys=[user_id])
    release             = db.relationship("Release", foreign_keys=[release_id])


class UserArtistIgnore(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    artist  = db.Column(db.String(255), index=True)

    user    = db.relationship("User", foreign_keys=[user_id])

###


class ApproximateTrackLength(db.Model):
    """
    As last.fm does not provide track length with scrobble (and querying each track
    length from api will be extremely slow approach), we can calculate approximate
    track lengths with scripts/calculateapproximatetracklengths.py
    """

    artist          = db.Column(db.String(length=255), primary_key=True)
    track           = db.Column(db.String(length=255), primary_key=True)
    length          = db.Column(db.Integer)

    stat_length     = db.Column(db.Integer)
    real_length     = db.Column(db.Integer)


class Coincidence(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    artist          = db.Column(db.String(length=255))
    track           = db.Column(db.String(length=255))
    users_uts       = db.Column(db.String(length=255))

###


class GuestVisit(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("user.id"))
    came            = db.Column(db.DateTime)
    came_data       = db.Column(db.PickleType(pickler=json))
    left            = db.Column(db.DateTime)
    left_data       = db.Column(db.PickleType(pickler=json))

    user            = db.relationship("User", foreign_keys=[user_id])

###


class Repeat(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("user.id"))
    artist          = db.Column(db.String(length=255))
    track           = db.Column(db.String(length=255))
    uts             = db.Column(db.Integer)
    total           = db.Column(db.Integer)

    user            = db.relationship("User", foreign_keys=[user_id])


class MilestoneCalculationTimestamp(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    uts             = db.Column(db.Integer)

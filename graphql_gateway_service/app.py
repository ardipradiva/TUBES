import os
from flask import Flask
from flask_graphql import GraphQLView
import graphene
from graphene import ObjectType, String, Int, List, Field, Schema
import requests
from datetime import datetime

app = Flask(__name__)

# Service URLs
EVENT_SUBMISSION_URL = "http://event_submission_service:5005"
EVENT_APPROVAL_URL = "http://event_approval_service:5006"
EVENT_STATUS_URL = "http://event_status_service:5007"
ROOM_BOOKING_URL = "http://room_booking_status_service:5009"

# GraphQL Types
class Event(graphene.ObjectType):
    event_id = graphene.Int()
    nama_event = graphene.String()
    deskripsi = graphene.String()
    tanggal_mulai = graphene.String()
    tanggal_selesai = graphene.String()
    status_approval = graphene.String()

class ApprovalLog(graphene.ObjectType):
    approval_id = graphene.Int()
    event_id = graphene.Int()
    tanggal_approval = graphene.String()
    status = graphene.String()
    catatan = graphene.String()

class RoomBookingStatus(graphene.ObjectType):
    booking_id = graphene.Int()
    event_id = graphene.Int()
    room_id = graphene.Int()
    status_booking = graphene.String()
    tanggal_update = graphene.String()

class EventStatus(graphene.ObjectType):
    event = Field(Event)
    approval_logs = List(ApprovalLog)
    room_booking_status = List(RoomBookingStatus)

# Input Types
class EventInput(graphene.InputObjectType):
    nama_event = graphene.String(required=True)
    deskripsi = graphene.String()
    tanggal_mulai = graphene.String(required=True)
    tanggal_selesai = graphene.String(required=True)

class ApprovalInput(graphene.InputObjectType):
    status = graphene.String(required=True)
    catatan = graphene.String()
    tanggal_approval = graphene.String(required=True)

class RoomBookingInput(graphene.InputObjectType):
    event_id = graphene.Int(required=True)
    room_id = graphene.Int(required=True)
    status_booking = graphene.String(required=True)
    tanggal_update = graphene.String(required=True)

# Queries
class Query(graphene.ObjectType):
    event_status = graphene.Field(EventStatus, event_id=graphene.Int(required=True))

    def resolve_event_status(self, info, event_id):
        try:
            response = requests.get(f"{EVENT_STATUS_URL}/events/{event_id}/status")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return None

# Mutations
class SubmitEvent(graphene.Mutation):
    class Arguments:
        event_data = EventInput(required=True)

    event = Field(Event)

    def mutate(self, info, event_data):
        try:
            response = requests.post(
                f"{EVENT_SUBMISSION_URL}/events",
                json=event_data
            )
            response.raise_for_status()
            return SubmitEvent(event=response.json())
        except Exception as e:
            return None

class ApproveEvent(graphene.Mutation):
    class Arguments:
        event_id = graphene.Int(required=True)
        approval_data = ApprovalInput(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, event_id, approval_data):
        try:
            response = requests.post(
                f"{EVENT_APPROVAL_URL}/events/{event_id}/approve",
                json=approval_data
            )
            response.raise_for_status()
            return ApproveEvent(success=True, message="Event approved successfully")
        except Exception as e:
            return ApproveEvent(success=False, message=str(e))

class UpdateRoomBooking(graphene.Mutation):
    class Arguments:
        booking_data = RoomBookingInput(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, booking_data):
        try:
            response = requests.post(
                f"{ROOM_BOOKING_URL}/room-booking-status",
                json=booking_data
            )
            response.raise_for_status()
            return UpdateRoomBooking(success=True, message="Room booking updated successfully")
        except Exception as e:
            return UpdateRoomBooking(success=False, message=str(e))

class Mutation(graphene.ObjectType):
    submit_event = SubmitEvent.Field()
    approve_event = ApproveEvent.Field()
    update_room_booking = UpdateRoomBooking.Field()

# Create Schema
schema = Schema(query=Query, mutation=Mutation)

# Add GraphQL endpoint
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True  # Enable GraphiQL interface
    )
)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True) 
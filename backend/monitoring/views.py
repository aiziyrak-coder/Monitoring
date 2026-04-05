import time

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from monitoring.models import Bed, Department, Device, Patient, Room
from monitoring.serializers import (
    BedCreateSerializer,
    BedSerializer,
    DepartmentCreateSerializer,
    DepartmentSerializer,
    DeviceCreateSerializer,
    DeviceSerializer,
    DeviceUpdateSerializer,
    RoomCreateSerializer,
    RoomSerializer,
)
from monitoring.services.patient_payload import all_patients_wire


class HealthView(APIView):
    def get(self, request):
        return Response(
            {
                "status": "ok",
                "uptime": time.monotonic(),
                "service": "clinic-monitoring-django",
            }
        )


class PatientsListView(APIView):
    def get(self, request):
        return Response(all_patients_wire())


class InfrastructureView(APIView):
    def get(self, request):
        return Response(
            {
                "departments": DepartmentSerializer(
                    Department.objects.all(), many=True
                ).data,
                "rooms": RoomSerializer(Room.objects.select_related("department"), many=True).data,
                "beds": BedSerializer(Bed.objects.all(), many=True).data,
                "devices": DeviceSerializer(Device.objects.select_related("bed"), many=True).data,
            }
        )


class DepartmentListCreateView(APIView):
    def post(self, request):
        ser = DepartmentCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = Department(name=ser.validated_data["name"])
        d.save()
        return Response(DepartmentSerializer(d).data, status=status.HTTP_201_CREATED)


class DepartmentDetailView(APIView):
    def delete(self, request, pk: str):
        Department.objects.filter(pk=pk).delete()
        return Response({"success": True})


class RoomListCreateView(APIView):
    def post(self, request):
        ser = RoomCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        dept = get_object_or_404(Department, pk=ser.validated_data["departmentId"])
        r = Room(name=ser.validated_data["name"], department=dept)
        r.save()
        return Response(RoomSerializer(r).data, status=status.HTTP_201_CREATED)


class RoomDetailView(APIView):
    def delete(self, request, pk: str):
        Room.objects.filter(pk=pk).delete()
        return Response({"success": True})


class BedListCreateView(APIView):
    def post(self, request):
        ser = BedCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        room = get_object_or_404(Room, pk=ser.validated_data["roomId"])
        b = Bed(name=ser.validated_data["name"], room=room)
        b.save()
        return Response(BedSerializer(b).data, status=status.HTTP_201_CREATED)


class BedDetailView(APIView):
    def delete(self, request, pk: str):
        Bed.objects.filter(pk=pk).delete()
        return Response({"success": True})


class DeviceListCreateView(APIView):
    def post(self, request):
        ser = DeviceCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        bed = None
        bid = ser.validated_data.get("bedId")
        if bid:
            bed = get_object_or_404(Bed, pk=bid)
        dev = Device(
            ip_address=ser.validated_data["ipAddress"],
            mac_address=ser.validated_data["macAddress"],
            model=ser.validated_data["model"],
            bed=bed,
            status="offline",
        )
        dev.save()
        return Response(DeviceSerializer(dev).data, status=status.HTTP_201_CREATED)


class DeviceDetailView(APIView):
    def put(self, request, pk: str):
        dev = get_object_or_404(Device, pk=pk)
        ser = DeviceUpdateSerializer(data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        if "bedId" in data:
            bid = data["bedId"]
            dev.bed = get_object_or_404(Bed, pk=bid) if bid else None
        if "status" in data:
            dev.status = data["status"]
        if "model" in data:
            dev.model = data["model"]
        if "ipAddress" in data:
            dev.ip_address = data["ipAddress"]
        if "macAddress" in data:
            dev.mac_address = data["macAddress"]
        dev.save()
        return Response(DeviceSerializer(dev).data)

    def delete(self, request, pk: str):
        Device.objects.filter(pk=pk).delete()
        return Response({"success": True})


class DeviceVitalsIngestView(APIView):
    """Qurilma (monitor) vitallarini qabul qilish — IP bo'yicha."""

    def post(self, request, ip: str):
        dev = Device.objects.filter(ip_address=ip).first()
        if not dev:
            return Response(
                {"error": "Device not registered"}, status=status.HTTP_404_NOT_FOUND
            )
        dev.status = "online"
        dev.last_seen_ms = int(time.time() * 1000)
        dev.save(update_fields=["status", "last_seen_ms"])

        body = request.data if isinstance(request.data, dict) else {}
        if dev.bed_id:
            p = Patient.objects.filter(bed_id=dev.bed_id).first()
            if p and body:
                for src, dst in (
                    ("hr", "hr"),
                    ("spo2", "spo2"),
                    ("nibpSys", "nibp_sys"),
                    ("nibpDia", "nibp_dia"),
                    ("rr", "rr"),
                    ("temp", "temp"),
                ):
                    if src in body:
                        setattr(p, dst, body[src])
                if "nibpTime" in body:
                    p.nibp_time_ms = int(body["nibpTime"])
                p.save()

        return Response({"success": True, "message": "Data received"})

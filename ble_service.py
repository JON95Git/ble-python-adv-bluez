import dbus
import dbus.mainloop.glib
import dbus.service
import array
from gi.repository import GLib
import sys

# Constants
BLUEZ_SERVICE_NAME = 'org.bluez'
ADAPTER_IFACE = BLUEZ_SERVICE_NAME + '.Adapter1'
LE_ADVERTISING_MANAGER_IFACE = BLUEZ_SERVICE_NAME + '.LEAdvertisingManager1'
GATT_MANAGER_IFACE = BLUEZ_SERVICE_NAME + '.GattManager1'
GATT_SERVICE_IFACE = BLUEZ_SERVICE_NAME + '.GattService1'
GATT_CHARACTERISTIC_IFACE = BLUEZ_SERVICE_NAME + '.GattCharacteristic1'
DBUS_OM_IFACE = 'org.freedesktop.DBus.ObjectManager'
DBUS_PROP_IFACE = 'org.freedesktop.DBus.Properties'

# Reversed UUID
SERVICE_UUID = 'c4e3409f-7723-42e0-ad14-bd1a23469eb9'

# DBus paths
BLUEZ_BUS_PATH = '/org/bluez/hci0'

class Service(dbus.service.Object):
    def __init__(self, bus, index):
        self.path = f"/com/example/service{index}"
        self.uuid = SERVICE_UUID
        self.primary = True
        self.characteristics = []
        dbus.service.Object.__init__(self, bus, self.path)

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature="ss", out_signature="v")
    def Get(self, interface, prop):
        if prop == "UUID":
            return self.uuid
        if prop == "Primary":
            return self.primary
        if prop == "Characteristics":
            return dbus.Array(self.characteristics, signature='o')

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature="sa{sv}", out_signature="")
    def Set(self, interface, properties):
        pass

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        return {
            "UUID": self.uuid,
            "Primary": self.primary,
            "Characteristics": dbus.Array(self.characteristics, signature='o')
        }

class Advertisement(dbus.service.Object):
    def __init__(self, bus, index):
        self.path = f"/com/example/advertisement{index}"
        self.bus = bus
        self.type = "peripheral"
        self.service_uuids = [SERVICE_UUID]
        self.manufacturer_data = None
        self.solicit_uuids = None
        self.service_data = None
        self.include_tx_power = True
        self.local_name = "MyDevice"
        self.flags = 0x06  # LE General discoverable mode, BR/EDR not supported
        dbus.service.Object.__init__(self, bus, self.path)

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature="ss", out_signature="v")
    def Get(self, interface, prop):
        if prop == "Flags":
            return dbus.Byte(self.flags)
        elif prop == "Type":
            return self.type
        elif prop == "ServiceUUIDs":
            return dbus.Array(self.service_uuids, signature='s')
        elif prop == "ManufacturerData":
            return self.manufacturer_data
        elif prop == "SolicitUUIDs":
            return self.solicit_uuids
        elif prop == "ServiceData":
            return self.service_data
        elif prop == "IncludeTxPower":
            return self.include_tx_power
        elif prop == "LocalName":
            return self.local_name

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature="sa{sv}", out_signature="")
    def Set(self, interface, properties):
        pass

    @dbus.service.method(DBUS_PROP_IFACE,
                         in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        properties = {
            "Flags": dbus.Byte(self.flags),
            "Type": self.type,
            "ServiceUUIDs": dbus.Array(self.service_uuids, signature='s'),
            "IncludeTxPower": self.include_tx_power,
            "LocalName": self.local_name
        }

        # Only add optional fields if they are not None
        if self.manufacturer_data is not None:
            properties["ManufacturerData"] = self.manufacturer_data
        if self.solicit_uuids is not None:
            properties["SolicitUUIDs"] = dbus.Array(self.solicit_uuids, signature='s')
        if self.service_data is not None:
            properties["ServiceData"] = self.service_data

        return properties

    def Release(self):
        pass

def register_advertisement(bus, adapter_path, advertisement):
    adapter = bus.get_object(BLUEZ_SERVICE_NAME, adapter_path)
    adapter_iface = dbus.Interface(adapter, LE_ADVERTISING_MANAGER_IFACE)
    adapter_iface.RegisterAdvertisement(advertisement, {}, 
        reply_handler=lambda: print("Advertisement registered"),
        error_handler=lambda e: print(f"Failed to register advertisement: {str(e)}"))

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()

    service = Service(bus, 0)
    advertisement = Advertisement(bus, 0)

    adapter_path = BLUEZ_BUS_PATH

    register_advertisement(bus, adapter_path, advertisement)

    try:
        GLib.MainLoop().run()
    except KeyboardInterrupt:
        print("Advertisement terminated")
        sys.exit(0)

if __name__ == "__main__":
    main()

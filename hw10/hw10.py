class Vehicle(object):
    def __init__(self, make, model, year, mileage, price):
        self.Make = make
        self.Model = model
        self.Year = year
        self.Mileage = mileage
        self.Price = price
        return
        
    def GetMake(self):
        return self.Make
        
    def SetMake(self, make):
        self.Make = make
        return
    
    def GetModel(self):
        return self.Model
        
    def SetModel(self, model):
        self.Model = model
        return
    
    def GetYear(self):
        return self.Year
        
    def SetYear(self, year):
        self.Year = year
        return
        
    def GetMileage(self):
        return self.Mileage
        
    def SetMileage(self, mileage):
        self.Mileage = mileage
        return
        
    def GetPrice(self):
        return self.Price
        
    def SetPrice(self, price):
        self.Price = price
        return
    
    def Display(self):
        print("Make:%s"%self.Make)
        print("Year:%i"%self.Year)
        print("Model:%s"%self.Model)
        print("Miles:%i"%self.Mileage)
        print("Price:%.2f"%self.Price)
        return
        
class Car(Vehicle):
    def __init__(self, make, model, year, mileage, price, doorNum):
        Vehicle.__init__(self, make, model, year, mileage, price)
        self.DoorNum = doorNum
        return
    
    def GetDoorNum(self):
        return self.DoorNum
        
    def SetDoorNum(self, doorNum):
        self.DoorNum = doorNum
        return 
    def Display(self):
        print("Inventory unit: Car")
        Vehicle.Display(self)
        print("Number of doors:%i"%self.DoorNum)
        return

class Truck(Vehicle):
    def __init__(self, make, model, year, mileage, price, driveType):
        Vehicle.__init__(self, make, model, year, mileage, price)
        self.DriveType = driveType
        return
        
    def GetDriveType(self):
        return self.DriveType
        
    def SetDriveType(self, driveType):
        self.DriveType = driveType
        return    
        
    def Display(self):
        print("Inventory unit: Truck")
        Vehicle.Display(self)
        print("Drive type:%s"%self.DriveType)
        return

class SUV(Vehicle):
    def __init__(self, make, model, year, mileage, price, capacity):
        Vehicle.__init__(self, make, model, year, mileage, price)
        self.Capacity = capacity
        return
        
    def GetCapacity(self):
        return self.Capacity
        
    def SetCapacity(self, capacity):
        self.Capacity = capacity
        return     
        
    def Display(self):
        print("Inventory unit: SUV")
        Vehicle.Display(self)
        print("Passenger Capacity:%i"%self.Capacity)
        return

class Inventory(object):
    def __init__(self):
        self.InventoryList = []
        return
    
    def addVehicle(self, vehicle):
        self.InventoryList.append(vehicle)
        return
    
    def Display(self):
        for vehicle in self.InventoryList:
            vehicle.Display()
            print('')
            print('')

class VehicleCreater(object):
    def __init__(self, type, make, model, year, mileage, price):
        self.VehicleObj = self.GetVehicleObj(type, make, model, year, mileage, price)
        return
    
    def GetVehicleObj(self, type, make, model, year, mileage, price):
        
        return

def main():
    inventory = Inventory()
    while True:
        vehicleObj = None
        type = vehicleTypeValidate()
        make, model, year, mileage, price = inputBasicAttribute()
        if type == 'car':
            doorNum = intValidate('doorNum')
            vehicleObj = Car(make, model, year, mileage, price, doorNum)
        elif type == 'truck':
            driveType = nonValidate('driveType')
            vehicleObj = Truck(make, model, year, mileage, price, driveType)
        elif type == 'suv':
            capacity = intValidate('capacity')
            vehicleObj = SUV(make, model, year, mileage, price, capacity)
        inventory.addVehicle(vehicleObj)
        isDoneEntering = isDoneEnteringData()
        if isDoneEntering:
            break
    inventory.Display()
    return

def vehicleTypeValidate():
    while True:
        print('input vehicle type:(car, truck or SUV)')
        type = input()
        type = type.lower()
        if type in ['car', 'truck', 'suv']:
            return type
        print('input type error!')
        
def inputBasicAttribute():
    make = nonValidate('make')
    model = nonValidate('model')
    year = intValidate('year')
    mileage = intValidate('mileage')
    price = floatValidate('price')
    return make, model, year, mileage, price
        
def nonValidate(attr):
    print('input %s:'%attr)
    value = input()
    return value
    
def intValidate(attr):
    while True:
        print('input %s:'%attr)
        value = input()
        try:
            value = int(value)
        except:
            print('input type error!(input int)')
            continue
        return value
        
def floatValidate(attr):
    while True:
        print('input %s:'%attr)
        value = input()
        try:
            value = float(value)
        except:
            print('input type error!(input int or float)')
            continue
        return value

def isDoneEnteringData():
    while True:
        print('is done entering vehicle data?(Y/N)')
        value = input()
        value = value.lower()
        if value in ['y', 'n']:
            if value == 'y':
                return True
            return False
        print('input value error!')

if __name__ == "__main__":
    main()

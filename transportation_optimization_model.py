from pyomo.environ import *
model = ConcreteModel()

model.Warehouses = Set(initialize=['Warehouse1', 'Warehouse2', 'Warehouse3'])
model.Customers = Set(initialize=['CustomerA', 'CustomerB', 'CustomerC', 'CustomerD'])

transportation_cost = {
    ('Warehouse1', 'CustomerA'): 10,
    ('Warehouse1', 'CustomerB'): 8,
    ('Warehouse1', 'CustomerC'): 12,
    ('Warehouse1', 'CustomerD'): 6,
    ('Warehouse2', 'CustomerA'): 9,
    ('Warehouse2', 'CustomerB'): 11,
    ('Warehouse2', 'CustomerC'): 13,
    ('Warehouse2', 'CustomerD'): 7,
    ('Warehouse3', 'CustomerA'): 14,
    ('Warehouse3', 'CustomerB'): 16,
    ('Warehouse3', 'CustomerC'): 10,
    ('Warehouse3', 'CustomerD'): 9,
}
model.TransportationCost = Param(model.Warehouses, model.Customers, initialize=transportation_cost)

product_types = ['ProductX', 'ProductY', 'ProductZ']
demand = {
    ('CustomerA', 'ProductX'): 20,
    ('CustomerA', 'ProductY'): 30,
    ('CustomerA', 'ProductZ'): 25,
    ('CustomerB', 'ProductX'): 15,
    ('CustomerB', 'ProductY'): 35,
    ('CustomerB', 'ProductZ'): 20,
    ('CustomerC', 'ProductX'): 25,
    ('CustomerC', 'ProductY'): 20,
    ('CustomerC', 'ProductZ'): 30,
    ('CustomerD', 'ProductX'): 10,
    ('CustomerD', 'ProductY'): 15,
    ('CustomerD', 'ProductZ'): 20,
}
model.Demand = Param(model.Customers, product_types, initialize=demand)

model.Shipment = Var(model.Warehouses, model.Customers, product_types, domain=NonNegativeReals)

def total_transportation_cost(model):
    return sum(model.Shipment[w, c, p] * model.TransportationCost[w, c] for w in model.Warehouses for c in model.Customers for p in product_types)
model.Objective = Objective(rule=total_transportation_cost, sense=minimize)

capacity = {
    ('Warehouse1', 'ProductX'): 50,
    ('Warehouse1', 'ProductY'): 60,
    ('Warehouse1', 'ProductZ'): 40,
    ('Warehouse2', 'ProductX'): 70,
    ('Warehouse2', 'ProductY'): 55,
    ('Warehouse2', 'ProductZ'): 50,
    ('Warehouse3', 'ProductX'): 40,
    ('Warehouse3', 'ProductY'): 30,
    ('Warehouse3', 'ProductZ'): 45,
}
model.CapacityConstraint = Constraint(model.Warehouses, product_types, rule=lambda model, w, p: sum(model.Shipment[w, c, p] for c in model.Customers) <= capacity[w, p])

delivery_time = {
    ('CustomerA', 'ProductX'): 2,
    ('CustomerA', 'ProductY'): 3,
    ('CustomerA', 'ProductZ'): 4,
    ('CustomerB', 'ProductX'): 3,
    ('CustomerB', 'ProductY'): 2,
    ('CustomerB', 'ProductZ'): 5,
    ('CustomerC', 'ProductX'): 4,
    ('CustomerC', 'ProductY'): 3,
    ('CustomerC', 'ProductZ'): 3,
    ('CustomerD', 'ProductX'): 2,
    ('CustomerD', 'ProductY'): 2,
    ('CustomerD', 'ProductZ'): 4,
}
model.DeliveryTimeConstraint = Constraint(model.Customers, product_types, rule=lambda model, c, p: sum(model.Shipment[w, c, p] for w in model.Warehouses) >= model.Demand[c, p])

from pyomo.opt import SolverFactory
opt = SolverFactory('scip')

results = opt.solve(model)

if results.solver.termination_condition == TerminationCondition.optimal:
    print("Optimization successful.")
else:
    print("Optimization failed. Solver status:", results.solver.termination_condition)

print("Total Transportation Cost:", model.Objective())

for w in model.Warehouses:
    for c in model.Customers:
        for p in product_types:
            print(f"Shipment of {p} from {w} to {c}: {model.Shipment[w, c, p].value}")

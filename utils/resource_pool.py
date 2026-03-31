from utils.constant import Resource

class ResourcePool:
    """Class pour stocker et manipuler les ressources d'un joueur
    """
    def __init__(self):
        self.resources = {r: 0 for r in Resource.real()}

    def add(self, resource, amount=1):
        self.resources[resource] += amount

    def remove(self, resource, amount=1):
        if self.resources[resource] < amount:
            raise ValueError("Pas assez de ressources")
        self.resources[resource] -= amount
    
    def get_amount(self, resource):
        """Get le nombre d'une certaine ressource
        Idem: self.resource[resource]

        Args:
            resource (Resource): la ressource

        Returns:
            int: le nombre
        """
        return self.resource[resource]

    def has(self, resource, amount=1):
        """Check si le ResourcePool à une certaine quantité de ressource

        Args:
            resource (Resource): La ressource
            amount (int, optional): montant. Defaults to 1.

        Returns:
            Bool: True or False
        """
        if resource == Resource.ANY:
            return self.total >= amount
        return self.resources[resource] >= amount
    
    def available(self, excluded=None):
        """Retourne les ressources que le joueur possède en quantité > 0.
        
        Args:
            excluded (set, optional): ressources à exclure
        
        Returns:
            list[Resource]: ressources disponibles [Resource.CALM, Resource.DEATH, ...]
        """
        excluded = excluded or set()
        excluded = excluded | {Resource.ANY}
        return [r for r, a in self.resources.items() if r not in excluded and a > 0]
    
    @property
    def total(self):
        excluded = {Resource.PEARL}
        return sum(a for r, a in self.resources.items() if r not in excluded)

    def __str__(self):
        return ", ".join(f"{r.value}:{self.resources[r]}" for r in Resource.real())
# Consulta de asiento reservado

Una aerolínea guarda los números de asiento reservados de un vuelo en un arreglo ordenado. Antes de ofrecer un asiento a un cliente, el servicio de reservas revisa si ya está ocupado.

**Especificaciones:**

- Los números de asiento son enteros ordenados de menor a mayor. Pueden repetirse.
- El arreglo puede tener hasta 1 millón de elementos; nunca es `null`, pero puede estar vacío.
- Se hacen muchas consultas sobre el mismo arreglo, así que importa no desperdiciar ciclos de CPU.

Implementa `static boolean isBooked(int[] seats, int seat)` en la clase `Solution`: devuelve `true` si `seat` está en `seats` y `false` en caso contrario.

**Ejemplo:**

```java
int[] seats = {12, 18, 33, 47};
Solution.isBooked(seats, 33)  // true
Solution.isBooked(seats, 20)  // false
```

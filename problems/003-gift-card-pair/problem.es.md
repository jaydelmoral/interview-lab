# Emparejar tarjeta de regalo

Una tienda en línea permite pagar un pedido con una tarjeta de regalo que debe usarse **exactamente**. Dados los precios (en centavos) de los artículos de un carrito y el saldo de la tarjeta, devuelve los **índices** de dos artículos distintos cuyos precios suman el saldo. Si hay varias parejas válidas, cualquiera se acepta. Si no hay ninguna, lanza `IllegalArgumentException`.

Implementa `int[] pairForBalance(int[] prices, int balance)` en la clase `Solution`. Complejidad objetivo: O(n).

```java
pairForBalance(new int[]{1200, 350, 899, 4500}, 1550)  // [0, 1]
pairForBalance(new int[]{500, 500, 250}, 1000)         // [0, 1]
```

# Dynamic Value Challenges for CTFd

It's becoming commonplace in CTF to see challenges whose point values decrease
after each solve.

This CTFd plugin creates a dynamic challenge type which implements this
behavior. Each dynamic challenge starts with an initial point value and then
each solve will decrease the value of the challenge until a minimum point value.
Within CTFd you are free to mix and match regular and dynamic challenges.

The current implementation requires the challenge to keep track of three values:

 * Initial - The original point valuation
 * Decay - The amount of solves before the challenge will be at the minimum
 * Minimum - The lowest possible point valuation

The value decay logic is implemented with the following math:

<!--
$$a=\textrm{max points}$$
$$b=\textrm{min points}$$
$$s=\textrm{solve threshold}$$

$$f(x)=\frac{b-a}{s^{2}}x^{2}+a$$
-->

![](https://raw.githubusercontent.com/CTFd/DynamicValueChallenge/master/function.png)

or in pseudo code:

```
value = (((minimum - initial)/(decay**2)) * (solve_count**2)) + initial
value = math.ceil(value)
```

If the number generated is lower than the minimum, the minimum is chosen
instead.

A parabolic function is chosen instead of an exponential or logarithmic decay function
so that higher valued challenges have a slower drop from their initial value.

# Installation

**REQUIRES: CTFd v1.0.5**

1. Clone this repository to `CTFd/plugins`. It is important that the folder is
not stored anywhere else, as the asset registrations depends on it being
directly beneath this folder.  You may however name the folder what ever you like.

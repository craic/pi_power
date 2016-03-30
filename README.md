# pi_power
Experiments in running portable Raspberry Pi systems from rechargeable batteries

The Raspberry Pi is a low cost, single board computer with reasonable performance and relatively low power
consumption. They are typically configured with the Linux operating system.

The Raspberry Pi family of boards have turned out to be very useful machines for standalone and/or
portable projects such as remote environment monitoring, cameras, etc.

But in order to be truly portable, a system needs to include a power source and a way to control
that power - such as a rechargeable battery, a charger, an on/off switch and some
way to monitor battery status.

Many people have worked on parts of this problem but there is no really good overall solution.

What I want is something equivalent to the way my iPhone works.
- I power it up from a cold state by holding down a button for a few seconds.
- To power it off I press the same button for a few seconds (and swipe an alert on the screen)
- The screen has an icon that shows me how much power remains in the battery
- I get an alert when that is running really low.
- If the battery runs out then the phone shuts down safely without any data corruption.
- To recharge the battery I just plug in a cable from a USB charger.



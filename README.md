# Peering-Performance-Degradation-Detection

# Authors

Arun Nandha Kumar S, Hewlett Packard Enterprise
Jayanth A, Hewlett Packard Enterprise

# Context

Enterprise Campus Network Switches hosts a suite of L3 - Routing Protocols and L2 Switching Protocols. A central theme of all the control plane protocols is that, they handshake -keep alive, probe peer status, abstract sliding window to keep their network information in sync. Though they have built with lot of resiliency, to automatically address different form of failures, link flap, h/w failures, daemon restart, great failure, congestion on I/O, newly added internal or external routes or IP addressing scheme change the mean time to recover can vary, and can also have a varying behavior per neighbor. This period is generally known as control plane convergence and only when the control plane is converged it can reflect the new behavior in the data plane. This period of instability will have traffic loss or black hole or dropped packets. This behavior can be exhibited due to numerous other reasons like intruder attack, low performing hardware. As this is critical problem, it becomes important to baseline and continuously monitor for any deviations for ensuring high available networks. It becomes very important to monitor for degradation and find more signatures and alert the administrator to further explore an underlying problem, before it occurs. So in that sense it becomes a predictive in nature of emerging degradations.

# Description

In peer to peer communicating protocols, most of the protocols have FSM states for protocol functionality and the behavior, and health of the protocol is determined by the FSM transitions of the protocol entity. Each FSM have several transitions and takes finite time between the transitions. Some of the transitions states provides key information about protocol peering status and it is required to alert the administrator to take further action based on these transition states. 

As per our solution we collect the FSM transitions for monitoring occurred for every 30 mins for monitoring protocols from the device and calculate (Min, Max, Mean and Average) transition time for the transition states and if any deviation is observed alter the administrator about the deviation observed for the peers.

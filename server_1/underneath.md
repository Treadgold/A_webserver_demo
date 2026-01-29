# The Network Stack Beneath HTTP

## Introduction

When we talk about HTTP, we're really talking about just one thin layer in a very tall stack. HTTP doesn't move bytes across the world by itself — it relies on TCP to break data into packets, resend anything that gets lost, and put everything back in order at the other end. And TCP, in turn, is standing on decades of networking technology: physical cables, fibre optics, radio waves, switches, routers, and protocols that decide how every packet finds its way through the internet.

Most of the time we don't think about any of this — and that's the miracle — because it all works so reliably that HTTP can pretend it's just sending a simple request and getting a response.

## What Sits Underneath TCP

From the application layer down to raw physics, here's what makes the internet work:

### Transport & Network Layer (Layer 3-4)

**TCP (Transmission Control Protocol)**
- Provides reliable, ordered delivery of data
- Handles packet sequencing and reassembly
- Implements flow control and congestion avoidance
- Manages connection establishment (three-way handshake) and teardown

**UDP (User Datagram Protocol)**
- Connectionless alternative to TCP
- Used for real-time applications where speed matters more than reliability
- No guarantees of delivery or ordering

### Core Networking Protocols (Layer 3)

**IP (Internet Protocol)**
- Addressing: assigns unique identifiers to devices (IPv4: 32-bit, IPv6: 128-bit)
- Routing: determines the path packets take across networks
- Fragmentation: breaks large packets into smaller pieces when needed
- IPv4 addresses are running out; IPv6 adoption continues globally

**ICMP (Internet Control Message Protocol)**
- Error reporting and diagnostics
- Powers utilities like `ping` (echo request/reply) and `traceroute`
- Reports unreachable hosts, time exceeded, and other network issues

**ARP / NDP (Address Resolution Protocol / Neighbor Discovery Protocol)**
- ARP: maps IPv4 addresses to MAC addresses on local networks
- NDP: performs the same function for IPv6, plus additional discovery tasks
- Essential for local network communication

### Local Network Technologies (Layer 2)

**Ethernet (IEEE 802.3)**
- Dominant wired local area networking standard
- Defines frame structure, addressing (MAC addresses), and collision detection
- Speeds range from 10 Mbps to 400 Gbps and beyond
- Variants include Fast Ethernet (100 Mbps), Gigabit Ethernet (1 Gbps), and 10 Gigabit Ethernet

**Wi-Fi (IEEE 802.11)**
- Wireless local area networking using radio frequencies
- Standards include 802.11ac (Wi-Fi 5) and 802.11ax (Wi-Fi 6/6E)
- Uses CSMA/CA (Carrier Sense Multiple Access with Collision Avoidance)
- Operates typically in 2.4 GHz and 5 GHz bands, with 6 GHz for Wi-Fi 6E

**VLANs (Virtual Local Area Networks)**
- Logical segmentation of physical networks
- Improves security, performance, and network management
- Defined by IEEE 802.1Q standard

**Switching**
- Operates at Layer 2 (data link layer)
- Forwards Ethernet frames based on MAC addresses
- Builds and maintains MAC address tables
- More efficient than hubs (which broadcast to all ports)

### Wide-Area and Routing Infrastructure

**Routers**
- Forward packets between different networks (Layer 3)
- Make decisions based on routing tables and protocols
- Connect your home network to your ISP, and ISPs to the broader internet

**BGP (Border Gateway Protocol)**
- The routing protocol of the internet's backbone
- How large networks (Autonomous Systems) exchange routing information
- Determines which paths data takes across the global internet
- Essential for internet resilience and redundancy

**NAT (Network Address Translation)**
- Allows multiple devices on a private network to share a single public IP
- Conserves IPv4 addresses
- Provides a basic level of security by hiding internal network structure
- Variants include SNAT, DNAT, and PAT (Port Address Translation)

**DNS (Domain Name System)**
- Translates human-readable domain names to IP addresses
- Hierarchical, distributed database system
- Critical infrastructure that makes the web user-friendly
- Operates primarily over UDP (port 53), with TCP for larger responses

### Physical Transmission Media (Layer 1)

**Copper Cables**
- *Twisted pair* (Cat5e, Cat6, Cat6a, Cat7): used for Ethernet, reduces electromagnetic interference
- *Coaxial cable*: used for cable internet and some legacy networks
- Limited by distance (typically 100m for Ethernet) and susceptible to interference

**Fibre-Optic Cables**
- Transmit data as pulses of light through glass or plastic fibres
- Enormous bandwidth potential (terabits per second)
- Immune to electromagnetic interference
- Long-distance transmission with minimal signal loss
- Two main types: single-mode (long distance) and multi-mode (shorter distances)

__Fun Fact:__   
The longest unregenerated terrestrial fiber optic link is over 10,358 kilometers, achieved by Telstra Corporation in Australia between Perth and Melbourne in 2015 according to Guinness World Records. This is quite remarkable because the signal traveled the entire distance and back without any regeneration.

**Radio Links**
- *Wi-Fi*: short-range wireless networking (typically 30-100m indoors)
- *Cellular*: mobile networks (4G LTE, 5G) with wide area coverage
- *Microwave*: point-to-point links for backhaul and remote connections
- *Satellite*: long-distance communication, useful for remote areas

**Submarine Cables**
- Intercontinental fibre-optic cables laid on the ocean floor
- Carry approximately 99% of international data traffic
- Hundreds of cables totaling over 1.4 million kilometres globally
- Modern cables can carry hundreds of terabits per second
- Critical infrastructure vulnerable to ship anchors, fishing nets, and earthquakes

### Supporting Hardware & Systems

**Network Interface Cards (NICs)**
- Hardware that connects a device to a network
- Handles the physical transmission and reception of data
- Contains a unique MAC address burned into the hardware
- Modern NICs often offload processing (TCP offload, checksumming)

**Optical Transceivers**
- Convert electrical signals to optical (light) signals and vice versa
- Various form factors: SFP, SFP+, QSFP, etc.
- Enable high-speed fibre-optic communication
- Hot-swappable in most enterprise equipment

**Switching ASICs (Application-Specific Integrated Circuits)**
- Specialized chips that perform packet switching at wire speed
- Enable modern switches to handle terabits of throughput
- Implement features like VLANs, QoS, and access control in hardware

**Repeaters and Amplifiers**
- Regenerate or amplify signals over long distances
- Overcome signal degradation and attenuation
- Critical for long-haul fibre-optic and copper links
- Optical amplifiers (like EDFAs) boost light signals without electrical conversion

## The Complete Picture

So when we say "a browser talks to a web server," what we really mean is: electrons, photons, and radio waves move through a global machine that TCP carefully choreographs so HTTP can feel simple.

Your HTTP request might travel through:
1. Your Wi-Fi router (radio waves → electrical signals)
2. Ethernet cables to your ISP's equipment
3. Fibre-optic cables across a city
4. A submarine cable across an ocean
5. Routers in multiple countries
6. Data center switching infrastructure
7. The server's network interface

All of this happens in milliseconds, with TCP ensuring every byte arrives intact and in order, while HTTP remains blissfully unaware of the complexity beneath it.

This abstraction — this ability to pretend the network is just a simple pipe — is one of computing's greatest achievements.

---

*The internet is not a cloud. It's millions of miles of cables, millions of devices, and millions of decisions per second, all working together to deliver your cat videos.*
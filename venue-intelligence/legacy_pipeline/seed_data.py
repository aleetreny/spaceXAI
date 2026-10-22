"""Research-sourced venue seed data, verified as directory/official page mentions on 2026-10-22.
This is a lead universe, NOT a list of bookable/available venues.
No personal data, images, protected aggregators' database exports, or Google Maps contents.
"""
from datetime import date

TH='https://www.towerhamlets.gov.uk/lgnl/community_and_living/halls_for_hire/halls_for_hire.aspx'
TH2=TH+'?hallsandvenues_List_GoToPage=2'
TH3=TH+'?hallsandvenues_List_GoToPage=3'
HK='https://communityhalls.hackney.gov.uk/venues'
LB='https://hire.lambeth.gov.uk/venues'
BR='https://spacehire.brent.gov.uk/spaces'
HR='https://haringey.gov.uk/housing/housing-resident-engagement/community-centres'

# One name per line from council directory. These are discovery leads; a sports hall, church or
# cultural facility is NOT inherently suitable for a laptop-based hackathon.
TH_NAMES = ["""
291 Gallery & Restaurant
4th Floor Studios
All Saints
Alpha Grove Community Centre
Artsadmin (formerly Curtain Theatre)
Attlee Centre
Bede Community Centre
Bernie Cameron Community Centre
Bethnal Green Community Centre
Bethnal Green Library
Bethnal Green Meeting House United Reformed Church
Bonner Primary School (Bethnal Green)
Bonner Primary School (Mile End)
Boro Bethnal Green Working Men's Club
Bow Arts - Nunnery Gallery
Bow Road Methodist Church
Bow School
Brady Arts and Community Centre
Butley Court Community Centre and Clubroom
Chicksand Friendly Club
Chisenhale Dance Space
Church of Christ & St John
Cruising Association - CA House
Darul Umman Centre
Davenant Centre
deafPlus
Docklands Sailing & Watersports Centre
Emmott Senior Citizen Lodge
Ensign Youth Club
Epainos Ministries (New Testament Church of God)
ExCeL London
Francis Lee Community Centre
Garrett Centre
Glamis Estate Tenants' Hall
Hanbury Hall
Hanbury Street Community Room
Harry Gosling Primary School
Hermitage School
Holiday Inn Whitechapel
""", """
Hub 67
Idea Store Bow
Idea Store Canary Wharf
Idea Store Chrisp Street
Idea Store Whitechapel
Ideal Centre
Island House Community Centre
John Orwell Sports Centre
Kirkland Centre
Langdon Park Sports & Community Centre
Lansbury HARCA Community Centre
Local History Library & Archives
London Executive Offices
Minerva Community Centre
MTHR
Neuron Pod, Centre of the Cell
Ocean Estate Tenants and Leaseholders Association
Osmani Centre
Oxford House Community Centre in Bethnal Green
Pitsea TRA Community Hall
Poplar After School Club (Poplar Play Centre)
Poplar, Blackwall and District Rowing Club
Queen Mary University of London - Event Venues
Rich Mix
Shadwell Basin Outdoor Activity Centre
SocietyLinks
Southern Grove Community Centre
St Anne's Church, Limehouse
St George in the East Church
St James the Less Church
St Johns Community Centre
St Margaret's House
St Matthias Community Centre
St Paul's Bow Common Church
St Paul's Church (Tower Hamlets directory)
St Peters North Community Centre
Sundial Centre
Tarling East Community Centre
The Ecology Pavilion, Mile End Park
""", """
The Linc Centre
The Space (Isle of Dogs)
Tiller Centre
Tramshed Community Centre
Tredegar Community Centre
Victoria Park Baptist Church
Whitechapel Gallery
Whitechapel Sports Centre
Wise Mind Tuition Centre
Wodenham Gardens Community Room
York Hall
Zander Court Club Room
"""]

# Pipe format: name|source_url|category|postcode|seated laptop max|theatre seated|standing|max price from|price unit|after18|weekend|notes
# No unknown field should be implicitly filled in; explicit yes flags only when published.
CURATED = r'''
Ramen Space|https://ramenclub.com/ramen-space/events/|coworking|E8 3GT|50|70|100|||yes|yes|Weekdays generally 18:00-21:30 and weekends generally 08:00-20:00; organizer must confirm specific date
Civo Tech Junction|https://www.civo.com/tech-junction|tech_event|EC2A 4AW||140|200|500|hour|yes|unknown|Public page header from £330/hour but commercial rental table £500/hour, min 2h; community nonprofit M-Th 18:00-21:00 hire free plus £200 cleaning; fibre 1Gb, wifi, full AV; confirm exact quote
Plexal Centre Stage|https://www.plexal.com/event-hire/|innovation_hub|E15 2GW||250||||unknown|unknown|Official page specifies theatre 250 and cabaret 100, bespoke AV and IT; evening/overnight access not confirmed in current operator page
Plexal Park|https://www.plexal.com/event-hire/|innovation_hub|E15 2GW||||||unknown|unknown|Breakout area; event hire includes IT support
Plexal Bleachers|https://www.plexal.com/event-hire/|innovation_hub|E15 2GW||||||unknown|unknown|Tiered informal presentation space
Plexal Legacy Place|https://www.plexal.com/event-hire/|innovation_hub|E15 2GW||||||unknown|unknown|Multi-config event space
IDEALondon Event Space|https://www.wilbelab.com/idealondon|innovation_hub|EC2A 2BB||100||1000|unspecified|unknown|unknown|69 Wilson Street; tech and startup focus; published event space for up to 100
CodeNode - Whole Venue|https://codenode.live/about-us/|tech_event|EC2M 7EB||300||||unknown|unknown|10 South Place; dedicated technology event venue
Encode Hub - Whole Venue|https://hirespace.com/Spaces/London/266430/Encode-Hub-Shoreditch/Whole-Venue/Events|tech_event|N1 6DA||250|300|||unknown|unknown|41 Pitfield Street; actual tech hackathon setting; third-party listing, permission required for reuse of content
The Gallery - Techspace Goswell Road|https://www.techspace.co/locations/goswell-road/events-at-the-gallery|coworking|EC1V 7DY||80|150|||unknown|unknown|140 Goswell Road; AV and optional breakout annex; 80 alone or 150 with adjacent space
The Lightwell - Techspace Worship Street|https://www.techspace.co/locations/worship-street/events|coworking|EC2A 2DX||50||||unknown|unknown|25 Worship Street; AV, adaptive event space, bandwidth options
The Loading Bay - Techspace Shoreditch|https://www.techspace.co/locations/shoreditch/events|coworking|||200||||unknown|unknown|Address conflict across operator official pages: 25 Luke Street EC2A 4DS versus Techspace listing at 130 Clifton Street EC2A 4HT; manager must confirm which site and max seated capacity
The Trampery Old Street|https://thetrampery.com/spaces/venue-hire/old-street/|coworking|EC1V 9EY||||||unknown|unknown|239 Old Street; venue, conference rooms and meeting rooms
The Hoxton Shoreditch Apartment|https://thehoxton.com/london/shoreditch/meeting-spaces/|hotel_event|E1 6AW||||||unknown|unknown|Meeting event rooms; seated laptops and out-of-hours to verify
Rainmaking Loft|https://rainmakingloft.com/uk/event-space.html|coworking|||||||unknown|unknown|Startup focused event space; confirm current trading status before contact
Impact Hub London Euston Event Space|https://london.impacthub.net/event-space-in-london|coworking|NW1 3DX||120|150|||unknown|unknown|1 Triton Square; 120 theatre seats, 60 cabaret, 150 standing; step-free AV 4K projection, breakout rooms, catering
Sustainable Ventures Event Space|https://southbank.london/venue-hire/sustainable-ventures|innovation_hub|||||||unknown|unknown|Belvedere Road; South Bank London workspace
SPACE4 Event Hire|https://space4.tech/hosting/|coworking|||||||unknown|unknown|Ethical tech coworking and hosted event space
Cavendish Venues - 22 Duchess Mews|https://www.cavendishvenues.co.uk/events/evening-weekends|conference|W1G 9DT||250||||yes|yes|Operator confirms evenings and weekends across locations
Cavendish Venues - 44 Hallam Street|https://www.cavendishvenues.co.uk/events/evening-weekends|conference|W1W 6JJ||250||||yes|yes|Operator confirms evening and weekend hire
Cavendish Venues - 1 America Square|https://www.cavendishvenues.co.uk/events/evening-weekends|conference|EC3N 2LB||270||||yes|yes|Operator confirms evening and weekend hire; 17 Crosswall
UCL - Torrington Place Training Centre|https://www.ucl.ac.uk/estates/ucl-venues/conference-and-venue-hire/torrington-place-training-centre|university|||||||unknown|unknown|External bookings offered
UCL - Tottenham Court Road Training Centre|https://www.ucl.ac.uk/estates/ucl-venues/conference-and-venue-hire|university|||||||unknown|unknown|External bookings offered
UCL - 20 Bedford Way / Logan Hall|https://www.ucl.ac.uk/estates/ucl-venues/conference-and-venue-hire|university|WC1H 0AL||||||unknown|unknown|20 Bedford Way, central Bloomsbury; lecture theatres and training spaces
UCL East - Marshgate|https://www.ucl.ac.uk/about/campuses-and-facilities/venues-and-halls-hire|university|E20||||||unknown|unknown|East London community and partner venue hire
LSE - Teaching Rooms|https://info.lse.ac.uk/staff/divisions/estates-division/room-booking-venue-hire/Secure/hire-conference-facilities|university|||80||||yes|yes|Teaching rooms from 18 to 80 and explicitly hireable evenings and weekends
LSE - Lecture Theatres|https://info.lse.ac.uk/staff/divisions/estates-division/room-booking-venue-hire/Secure/hire-conference-facilities|university|||130||||restricted|yes|Mainly weekends and vacations, weekday evening events considered case by case
LSE - Harvard Theatres|https://info.lse.ac.uk/staff/divisions/estates-division/room-booking-venue-hire/Secure/hire-conference-facilities|university|||90||||unknown|unknown|49-90 theatre seats; LSE campus
King's College London - London Bridge Venues|https://www.kcl.ac.uk/kingsvenues/locations/kings-venues-at-london-bridge/venue-hire|university|||||||unknown|unknown|KCL venue hire department
University of London - Senate House MacMillan Hall|https://www.london.ac.uk/about/services/conference-event-hire|university|||220||||unknown|unknown|Large flat-floor hall in Bloomsbury
University of London - Senate House Beveridge Hall|https://www.london.ac.uk/about/services/conference-event-hire|university|||375||||unknown|unknown|Theatre and presentation hall
Imperial Venues - Queen's Tower Rooms and Terrace|https://www.imperialvenues.co.uk/events/conference/|university|||470|640|||unknown|unknown|Classroom 200; theatre 470; overall max 640 varies by layout
Imperial Venues - City and Guilds Lecture Theatres|https://www.imperialvenues.co.uk/events/conference/|university|||350|380|||unknown|unknown|Four lecture theatres with AV
Imperial College - White City Event Venues|https://www.imperial.ac.uk/media/imperial-college/administration-and-support-services/events-and-hospitality/public/Imperial-Showcase---Event-Venues---Jan-2025.pdf|university|W12||||||unknown|unknown|Need individual room extraction from brochure
SOAS - Campus Venue Hire|https://www.soas.ac.uk/conference-and-venue-hire|university|WC1H||||||unknown|unknown|External venue bookings
Goldsmiths - Campus Event Spaces|https://www.gold.ac.uk/conference-services/spaces/|university|SE14||||||unknown|unknown|Arts university venue spaces
University of Greenwich - Avery Hill Conference Venues|https://www.gre.ac.uk/estates-facilities/commercial-catering-and-events/find-a-venue/conferences-avery-hill|university|SE9||||||unknown|unknown|Modern meeting and conference spaces
University of Westminster - Venue Hire|https://www.westminster.ac.uk/about-us/visit-us/venues-and-accommodation|university|||||||unknown|unknown|Professional spaces for hire
University of East London - Venue Hire|https://www.uel.ac.uk/about/venue-hire|university|||||||unknown|unknown|External space hire; independently verify live page
Regent's University London - Regent's Events|https://regentsevents.co.uk/event-type/training-education/|university|NW1||||||unknown|unknown|Training and education events
Queen Mary University London - Events & Hospitality|https://www.qmul.ac.uk/events-hospitality/|university|E1||||||unknown|unknown|Over 100 purpose-built meeting facilities according to Tower Hamlets directory
RCP London Events|https://www.rcp.ac.uk/about-us/venue-hire/|conference|NW1||||||unknown|unknown|Royal College of Physicians meeting and conference venue
Royal Society - Venue Hire|https://royalsociety.org/venue-hire-central-london/|conference|SW1Y||||||unknown|unknown|Royal Society in Carlton House Terrace; formal event spaces
IET London Savoy Place - Meeting Rooms|https://savoyplace.theiet.org/plan-your-event/meeting-and-training-venue/|conference|WC2R||||||unknown|unknown|Dedicated AV and training/meeting facilities
London Film School - Venue Hire|https://lfw.org.uk/hire/|university|WC2||||||unknown|unknown|Film school teaching studios and screening spaces
Workspace - Salisbury House Eventspace|https://www.workspace.co.uk/eventspace|coworking|EC2M 5QD||||||unknown|unknown|114 London Wall; events and conferences
The Mills Fabrica - King's Cross Event Space|https://www.themillsfabrica.com/spaces/event-space-london/|innovation_hub|N1||||||unknown|unknown|King's Cross innovation hub event hire
Kings Place Events|https://kingsplaceevents.co.uk/|conference|N1||||||unknown|unknown|Large multi-room event venue near King's Cross
Kings House Venue Hire|https://www.kingshouse.org.uk/hire|conference|N1||||||unknown|unknown|Two minutes from King's Cross, rooms for hire
30 Euston Square - Camden Suite|https://hirespace.com/Spaces/London/282952/30-Euston-Square/The-Camden-Suite/Conferences|conference|NW1||||||unknown|unknown|Venue in Euston; third-party listing
British Library - Knowledge Centre|https://www.bl.uk/services/commercial-venue-hire|conference|NW1|||255|8500|day|yes|yes|Evening 18:00-22:00 on Tue/Wed; weekends 08:30-17:00; weekend day price from £8,500
British Library - Pigott Theatre|https://www.bl.uk/services/commercial-venue-hire|conference|NW1||255||8500|day|yes|yes|Part of Knowledge Centre; precise price depends on configuration
British Library - Harley Room|https://www.bl.uk/services/commercial-venue-hire|conference|NW1||12||950|day|yes|no|Not weekend hireable per venue schedule; evening at additional pricing
The Design Museum - Event Spaces|https://designmuseum.org/venue-hire/event-spaces|museum|W8||||||unknown|unknown|Several contemporary private event rooms
British Museum - BP Lecture Theatre|https://www.britishmuseum.org/commercial/venue-hire/bp-lecture-theatre|museum|WC1B||||||unknown|unknown|Lecture room for hire
National Gallery - Event Spaces|https://www.nationalgallery.org.uk/venue-hire/event-spaces|museum|WC2N||||||unknown|unknown|Gallery and private hire rooms; laptop work suitability to verify
Science Museum - Events Spaces|https://www.sciencemuseum.org.uk/venue-hire|museum|SW7||||||unknown|unknown|Conference and museum gallery spaces
London Museum - London Wall Event Rooms|https://www.londonmuseum.org.uk/commercial/venue-hire/spaces/|museum|EC2Y||||||unknown|unknown|Museum 150 London Wall
Courtauld - Venue Hire|https://courtauld.ac.uk/venue-hire/|museum|WC2R||||||unknown|unknown|Venue hire for receptions and events
Whitechapel Gallery - Events|https://www.whitechapelgallery.org/support/venue-hire/|museum|E1||||||yes|unknown|Tower Hamlets council says evening receptions available
V&A - Venue Hire|https://www.vam.ac.uk/info/venue-hire|museum|SW7||||||unknown|unknown|Event spaces, some unsuitable for laptop hackathon
Rich Mix - Private Hire|https://richmix.org.uk/hire/|arts|E1||||||unknown|unknown|Independent arts centre and boutique event rooms
The Castle Cinema - Private Hire|https://thecastlecinema.com/private-hire/|cinema|E5||||||unknown|unknown|Screening and private events
Electric Cinema - Private Hire|https://www.electriccinema.co.uk/private-hire/|cinema|||||||unknown|unknown|Cinemas in London, hire independently
Coldharbour Blue - Private Hire|https://www.coldharbourblue.com/private-hire/|cinema|SW9||||||unknown|unknown|Independent cinema in Brixton
Close-Up Film Centre - Venue Hire|https://www.closeupfilmcentre.com/venue-hire/|cinema|E1||||||unknown|unknown|Cinema in Shoreditch
Prince Charles Cinema - Screen 1|https://princecharlescinema.com/cinema-hire/|cinema|WC2H||300||||unknown|unknown|Auditorium and projection; limited laptop desks
Kiln Theatre - Event Spaces|https://kilntheatre.com/our-story/hire/|arts|NW6||||||unknown|unknown|Theatre and flexible event rooms
BFI IMAX - Venue Hire|https://www.bfi.org.uk/venue-hire/hiring-bfi-imax|cinema|SE1||||||unknown|unknown|Large screening auditorium, unlikely desk-ready
Tanner Warehouse|https://www.tannerwarehouse.co.uk/events/corporate/|warehouse|SE1 3UD||||||unknown|unknown|50 Bermondsey Street; corporate events
Copeland Park - Unit 08|https://www.copelandpark.com/venue/unit-08/|warehouse|SE15||||||unknown|unknown|11,500 sqft dry-hire, infrastructure to verify
Deptford Storehouse|https://spacesstories.com/space/deptford-storehouse/|warehouse|SE8||||||unknown|unknown|Very large blank canvas; infrastructure and economics not ideal for typical hackathon
Number 90 Corporate|https://number90corporate.co.uk/|arts|E9||||||unknown|unknown|Hackney Wick venue
Grow Hackney - Events|https://www.growhackney.co.uk/spaces|arts|E9||||||unknown|unknown|Hackney Wick multilevel canal venue
Vittoria Wharf Studio|https://www.vittoriawharfstudio.com/|arts|E9||||||unknown|unknown|Hackney Wick cultural venue
The Art House|https://thearthouse.live/|arts|||||||unknown|unknown|Converted warehouse event space
Studio Spaces - Events|https://studio-spaces.com/|warehouse|E1||||||unknown|unknown|Former industrial factory, ~743 sqm
Deptford Lounge - Spaces|https://www.thealbany.org.uk/for-business/the-albany-conference-venue-in-south-east-london-3-2-2|community|SE8||||||unknown|unknown|Conference and community meeting spaces
Hoxton Docks|https://venues.london/venue/hoxton-docks/|warehouse|E2||300|700|||unknown|unknown|Warehouse venue, higher budget likely
Sundial Centre - Tower Hamlets|https://www.towerhamlets.gov.uk/lgnl/community_and_living/halls_for_hire/Sundial_centre.aspx|community|E1||50||||unknown|unknown|Hall capacity 50, council offer
The Old Laundry - Stockwell|https://www.stockwellmatters.org/hire|community|SW8||||||unknown|unknown|Stockwell Matters charity space hire
Coin Street Conference Centre|https://www.coinstreet.org/venue-hire|conference|SE1||||||unknown|unknown|Southbank social enterprise conference centre
Anomalous Space|https://anomalous.co.uk/space|coworking|N1||||||unknown|unknown|Flexible event space near Angel
The Arc Centre, Islington|https://hirespace.com/Spaces/London/166158/The-Arc-Centre-Islington/Main-Room/Business|community|N1 7DF||||||unknown|unknown|98B Saint Paul Street
The AHOY Centre - Main Function Room|https://ahoy.org.uk/facility-hire/|community|SE8||||||unknown|unknown|Function room with river view
Paddington Works|https://www.paddingtonworks.com/|coworking|W2||||||unknown|unknown|Co-working events, meeting rooms production facilities
Landing Canary Wharf|https://landingcanarywharf.com/about-us/|conference|E14||||||unknown|unknown|Canary Wharf event venue
Level39 - The Sandbox|https://level39.co/event-spaces/venue-hire/|innovation_hub|E14||||||unknown|unknown|Canary Wharf event space; technology community
10 York Road - WeWork Auditorium|https://www.wework.com/en-GB/info/the-auditorium-at-10-york-rd|coworking|SE1||||||unknown|unknown|Waterloo event auditorium
Storey Club|https://storey.co.uk/storey-club/|coworking|||||||unknown|unknown|Multiple London operator event spaces
Oneder - Meeting & Events|https://www.withoneder.com/meeting-and-events/|coworking|||||||unknown|unknown|Operator across London; locations to expand
The Lantern by Tonik|https://www.thelanternbytonik.com/|conference|SE1||||||unknown|unknown|Community venue London Bridge
The Bridge - Waterloo Room|https://www.thebridge-uk.org/hire-spaces|community|SE1||||||unknown|unknown|Waterloo meeting breakout room
Soho Works - The Lofts at Shoreditch House|https://www.sohohouse.com/houses/shoreditch-house/event-spaces|coworking|E1 6AW||100|250|||unknown|unknown|Available for public hire unlike members-only Library/Back Deck
The Trampery - General Venues|https://thetrampery.com/spaces/venue-hire/|coworking|||||||unknown|unknown|Multiple London sites, avoid duplicate operator locations
Soho Works - White City|https://www.sohoworks.com/white-city/|coworking|W12||||||unknown|unknown|Workspaces; external event hire to verify
Studio Y - Spacemade|https://www.spacemade.co/locations/london/studio-y/|coworking|W11||||||unknown|unknown|Notting Hill coworking; room hires unverified
Scale Space White City|https://www.scalespace.co.uk/|innovation_hub|W12||||||unknown|unknown|University linked scaleup workspace; event hire unverified
Imperial Incubator - White City|https://imperialincubator.com/our-locations/white-city/|innovation_hub|W12 7RZ||||||unknown|unknown|Business incubator, event bookings must be checked
Blue Garage Innovation Hub|https://www.bluegarage.org/|innovation_hub|SE13 7HA||||||unknown|unknown|Lewisham maker space and coworking, event hire status unverified
Hackney Depot|https://www.hackneydepot.com/|arts|E8||||||unknown|unknown|Creative studios and venue
Open House Hackney|https://www.openhousehackney.com/|arts|E9||||||unknown|unknown|Creative communal space
Arbeit Studios - Event Spaces|https://www.arbeit.org.uk/exhibitons-and-events|arts|||||||unknown|unknown|Managed studios and gallery/event spaces
The Yard Theatre - Event Hire|https://www.theyardtheatre.co.uk/hire-the-yard|arts|E9||||||unknown|unknown|Hire venue for launches and events
Wick Studio|https://www.wickstudio.uk/|arts|E9||||||unknown|unknown|Studio, small photographic space not standard 50-person hackathon
St Mary's Islington - Venue Hire|https://www.stmaryislington.org/ourspaces|community|N1||||||unknown|unknown|Meeting rooms in Islington
Hilldrop Community Centre|https://www.hilldrop.org.uk/hall-hire|community|N7||||||unknown|unknown|Three hire spaces
Hugh Cubitt Community Centre|https://directory.islington.gov.uk/kb5/islington/directory/service.page?id=JoOZX1C5MmA|community|N1||40||||unknown|unknown|Hall for up to 40
West Library Hall - Islington|https://www.islington.gov.uk/libraries-arts-and-heritage/libraries/your-local-libraries/west-library|library|N1 1BD||100||||unknown|unknown|Library confirms meeting hall available for hire
London Chinese Community Centre - Rooms|https://ccc.org.uk/venue-hire-and-advertising/venue-for-hire/|community|WC2||||||unknown|unknown|Three multifunctional hire rooms
Camden - Swiss Cottage Library Hire|https://www.camden.gov.uk/halls-for-hire|library|NW3||||||yes|unknown|Camden libraries offer after-hours hire, check which location
Camden - Kentish Town Library Hire|https://www.camden.gov.uk/halls-for-hire|library|NW5||||||yes|unknown|Camden libraries offer after-hours hire, check which location
Camden - Queens Crescent Library Hire|https://www.camden.gov.uk/halls-for-hire|library|NW5||||||yes|unknown|Camden libraries offer after-hours hire, check which location
Camden - Holborn Library Hire|https://www.camden.gov.uk/halls-for-hire|library|WC1||||||yes|unknown|Camden libraries offer after-hours hire, check which location
Camden - Kilburn Library Hire|https://www.camden.gov.uk/halls-for-hire|library|NW6||||||yes|unknown|Camden libraries offer after-hours hire, check which location
Westminster - Victoria Library Large Events Room|https://www.westminster.gov.uk/victoria-library|library|SW1V||70||300|half_day|restricted|yes|Published evening extension by request; Saturday daytime; WiFi, projector, PA, catering
Westminster - Victoria Library Small Room|https://www.westminster.gov.uk/victoria-library|library|SW1V||25||||unknown|unknown|Published room temporarily unavailable in older page; must confirm current status
Westminster - Charing Cross Library Room Hire|https://www.westminster.gov.uk/leisure-libraries-and-community/libraries/rooms-hire-libraries-and-archives-centre|library|WC2||||||unknown|unknown|Public library room hire
Westminster - Church Street Library Room Hire|https://www.westminster.gov.uk/leisure-libraries-and-community/libraries/rooms-hire-libraries-and-archives-centre|library|NW8||||||unknown|unknown|Public library room hire
Westminster - Maida Vale Library Room Hire|https://www.westminster.gov.uk/leisure-libraries-and-community/libraries/rooms-hire-libraries-and-archives-centre|library|W9||||||unknown|unknown|Public library room hire
Westminster - Mayfair Library Room Hire|https://www.westminster.gov.uk/leisure-libraries-and-community/libraries/rooms-hire-libraries-and-archives-centre|library|W1||||||unknown|unknown|Public library room hire
Westminster - Westminster Business Library Hire|https://www.westminster.gov.uk/leisure-libraries-and-community/libraries/rooms-hire-libraries-and-archives-centre|library|SW1||||||unknown|unknown|Public library room hire
Westminster - Reference Library (Isaac Newton Room)|https://www.westminster.gov.uk/leisure-libraries-and-community/libraries/rooms-hire-libraries-and-archives-centre/isaac-newton-room-westminster-reference-library|library|WC2N||12||||no|yes|Weekday only until 18:00; Saturday daytime only; small room
Lambeth - Clapham Library Whole Library|https://hire.lambeth.gov.uk/venues/343-clapham-library/4530-whole-library|library|SW4 7DB||||||unknown|unknown|Mary Seacole Centre; booking platform
Lambeth - Durning Library Whole Library|https://hire.lambeth.gov.uk/venues/344-durning-library/5063-whole-library|library|SE11 4HF||||||unknown|unknown|167 Kennington Lane
Merton - Wimbledon Library Rooms|https://www.merton.gov.uk/leisure-recreation-and-culture/hallhire/wimbledon-library-activity-area|library|SW19||||||unknown|unknown|Flexible rooms for meetings and workshops
Merton - Mitcham Library|https://www.merton.gov.uk/mertonvenues/indoor-venues/mitcham-library|library|CR4||||||yes|unknown|Explicit out-of-hours room hire
Merton - Arts Space Mitcham|https://www.merton.gov.uk/mertonvenues/indoor-venues/arts-space-mitcham|arts|CR4||||||unknown|unknown|Arts meeting venue
Southwark - Peckham Library Pod 1|https://services.southwark.gov.uk/leisure-facility-hire-and-bookings/8/peckham-library-pod-1?c=141|library|SE15||50||67.4|hour|unknown|unknown|Council listing, up to 50; £67.4/hour
Southwark - Una Marson Community Space|https://services.southwark.gov.uk/leisure-facility-hire-and-bookings/37/una-marson-community-space|community|SE1||60||70|hour|unknown|unknown|Council listing £70/hr; community discount may apply
Tower Hamlets - Ideal Centre|https://www.towerhamlets.gov.uk/lgnl/community_and_living/halls_for_hire/Ideal-Centre.aspx|community|E1 4UN||100||40|hour|yes|restricted|Tue/Thu to midnight; weekends 18:00-midnight; weekday Monday/Wednesday/Friday ends 16:30
Knowledge Schools Trust - Palingswick House|https://www.wlfs.org/Hiring-Space/|school|W6 9LP||||||yes|yes|After 18:00 weekdays in term; full day weekends and holidays
Knowledge Schools Trust - Franklin House|https://www.wlfs.org/Hiring-Space/|school|W6 9JP||||||yes|yes|After 18:00 weekdays in term; full day weekends and holidays
The London Academy School - Event Hire|https://www.londonacademy.org.uk/about/hiring-the-academy/|school|||||||yes|yes|Evenings and weekends; check precise locations
Highgate School - Venue Hire|https://www.highgateschool.org.uk/book-hire/venue-hire/|school|N6||||||unknown|unknown|Hired facilities
Global Academy - Venue Hire|https://globalacademy.com/about/hire/|school|||||||unknown|unknown|Education facilities hire
St Paul's School - Facilities Hire|https://www.stpaulsschool.org.uk/about-st-pauls/facilities-hires/|school|SW13||||||unknown|unknown|Barnes; building and event rooms
Winchmore School - Lettings|https://www.winchmore.enfield.sch.uk/page/?pid=11&title=Lettings|school|N21||||||yes|unknown|School lists evening hire
Alperton Community School - Venue Hire|https://www.alperton.brent.sch.uk/our-school/community/lettings/|school|HA0||||||unknown|unknown|Conference and reception hire
City of London School - Venue Hire|https://www.cityoflondonschool.org.uk/venue-hire2/|school|EC4V||||||unknown|unknown|Riverside central London campus
Regent High School - Lettings|https://www.regenthighschool.org.uk/Lettings-02062016144048/|school|NW1||||||unknown|unknown|Conference and meeting hire
Stratford School Academy - Facilities Hire|https://www.stratfordschoolacademy.com/738/facilities-hire|school|E7||||||unknown|unknown|Facilities available for hire
Paddington Academy - Venue Hire|https://www.paddington-academy.org/lettings|school|W2||||||unknown|unknown|Studio theatre and learning spaces
Sedgehill Academy - Auditorium|https://www.hallshire.com/halls/view/6633/sedgehill-academy-auditorium-stage|school|SE6||500||||unknown|unknown|Catford, third-party advert
Electra House - Lecture Theatre|https://www.efigroup.ac.uk/venue-hire|training_centre|EC2M 6SE||100||||yes|yes|Fixed banked 100 theatre seats with integrated desks; weekdays 18:00-21:00 weekends 09:00-21:00; min half day
Electra House - Showspace|https://www.efigroup.ac.uk/venue-hire|training_centre|EC2M 6SE||50|80|||yes|yes|Flexible show space capacity 50 to 80 based on layout; weekday evenings and weekend hire; AV and courtyard
Electra House - Domed Boardroom|https://www.efigroup.ac.uk/venue-hire|training_centre|EC2M 6SE||14||||yes|yes|14 seated at central board table, video meeting capability, kitchenette; off-peak hire
Electra House - Training Suites (four classrooms)|https://www.efigroup.ac.uk/venue-hire|training_centre|EC2M 6SE||31||||yes|yes|Four distinct classrooms each 13-31 classroom seated; separate individual room capacities cannot be assigned yet
Impact Hub London Euston - Small Meeting Rooms|https://london.impacthub.net/event-space-in-london|coworking|NW1 3DX||||||unknown|unknown|Operator advertises smaller boardroom meetings but room-by-room counts and availability not listed
Huckletree - The Landing Bishopsgate|https://www.huckletree.com/hubs/hire-event-spaces/london|coworking|EC2M||80|80|||unknown|unknown|Operator event rooms: up to 80 participants; exact seating mix and schedule on enquiry
Huckletree - The Common Liverpool Street|https://www.huckletree.com/hubs/hire-event-spaces/london|coworking|EC2M||100|100|||unknown|unknown|Operator event hire: 100 seats or standing, layout and laptop power unknown
Huckletree - The Parlour Oxford Circus|https://www.huckletree.com/hubs/hire-event-spaces/london|coworking|W1B||40|80|||unknown|unknown|40 seated and 80 standing; event space hire advertised
Huckletree - The Penthouse Lounge Kensington|https://www.huckletree.com/hubs/hire-event-spaces/london|coworking|W8||60|60|||unknown|unknown|Event room 60 people, operator direct listing
Huckletree - The Terrace Westminster|https://www.huckletree.com/hubs/hire-event-spaces/london|coworking|SW1P||40|70|||yes|yes|Operator says evenings and weekends only; 40 seated, 50-70 standing
Huckletree - Elwood Cafe Soho|https://www.huckletree.com/hubs/hire-event-spaces/london|coworking|W1F||20|50|||yes|yes|Operator says evenings and weekends only; 20 seated and 50 standing
Huckletree - Town Hall Liverpool Street|https://www.huckletree.com/hubs/hire-event-spaces/london|coworking|EC2M||22||||unknown|unknown|22 person event/meeting space hire
Huckletree - The Forum Leadenhall (future)|https://www.huckletree.com/hubs/hire-event-spaces/london|coworking|EC3V||200||||unknown|unknown|Coming soon when reviewed; NOT an operational listing
Second Home Spitalfields - The Rooftop|https://secondhome.io/space/spitalfields-the-rooftop/|coworking|E1||50|100|500|hour|yes|yes|Explicit evening and weekend hire; three-hour minimum; 50 seated 100 standing; VAT excluded
Second Home Spitalfields - The Auditorium|https://secondhome.io/venues/|coworking|E1||120|150|||unknown|unknown|120 seated or 150 standing; exact weekend booking unknown
Second Home Spitalfields - The Cafe|https://secondhome.io/venues/|coworking|E1||45|80|||unknown|unknown|45 seated 80 standing; café venue hire advertised
Second Home Spitalfields - Hanbury Studio|https://secondhome.io/venues/|coworking|E1||45||||unknown|unknown|Studio hire, 45 seated; laptop layout to verify
Second Home Spitalfields - The Study|https://secondhome.io/venues/|coworking|E1||35|40|||unknown|unknown|20 to 35 seated, 40 standing; meeting and events
Second Home Spitalfields - Workshop Space|https://secondhome.io/venues/|coworking|E1||35||||unknown|unknown|Workshop room 35 seated
Second Home Holland Park - The Courtyard|https://secondhome.io/venues/|coworking|W11||40|60|||unknown|unknown|40 seated or 60 standing; private hire inventory
Second Home Holland Park - Libreria Bookshop|https://secondhome.io/venues/|coworking|W11|||50|||unknown|unknown|50 standing; may be unsuitable for plugged-in hackathon
x+why - Fivefields Victoria Event Space|https://www.xandwhy.co.uk/memberships-type/event-spaces|coworking|SW1W||100||300|hour|unknown|unknown|Victoria; capacity 100, rates from 300 GBP/hour, may exclude VAT
x+why - One Great Cumberland Place Event Space|https://www.xandwhy.co.uk/memberships-type/event-spaces|coworking|W1H||120||750|hour|unknown|unknown|Marble Arch; 120 capacity, rate from 750 GBP/hour
x+why - Chiswick Works Event Space|https://www.xandwhy.co.uk/memberships-type/event-spaces|coworking|W4||40||100|hour|unknown|unknown|Chiswick; 40 capacity, hire from 100 GBP/hour
x+why - The People's Mission Hall|https://www.xandwhy.co.uk/memberships-type/event-spaces|coworking|E1||||||unknown|unknown|Whitechapel/Aldgate East; event space offered; capacity unknown
x+why - The Fulwood|https://www.xandwhy.co.uk/memberships-type/event-spaces|coworking|WC1V||||||unknown|unknown|Holborn; event meeting space candidate; hire schedule unknown
x+why - 22 Bishopsgate Event Space|https://www.xandwhy.co.uk/memberships-type/event-spaces|coworking|EC2N||||||unknown|unknown|City coworking event space at 22 Bishopsgate; capacity unknown
x+why - Arding & Hobbs Event Space|https://www.xandwhy.co.uk/memberships-type/event-spaces|coworking|SW11||||||unknown|unknown|Clapham Junction; event space advertised
London Academy - Evening and Weekend Academy Hire|https://www.londonacademy.org.uk/about/hiring-the-academy/|school|NW9||||||yes|yes|School makes campus facilities available public hire every evening/weekends
The Mills Fabrica - King's Cross Event Space|https://www.themillsfabrica.com/spaces/event-space-london/|innovation_hub|N1C||||||unknown|unknown|King's Cross startup hub with operator advertised event space
Landing Canary Wharf - Event Venue|https://landingcanarywharf.com/about-us/|coworking|E14||||||unknown|unknown|Purpose-built events and coworking venue; exact schedule unverified
The Lantern by Tonik - London Bridge|https://www.thelanternbytonik.com/|arts|SE1||||||unknown|unknown|London Bridge creative communal venue hire
Space4Tech - Tech Community Event Room|https://space4.tech/hosting/|coworking|N4||||||unknown|unknown|Potential parent room of SPACE4 Event Hire; duplicate risk needs review
Huckletree London - General Event Spaces|https://www.huckletree.com/hubs/hire-event-spaces/london|coworking|||||||unknown|unknown|Operator directory parent row; potential duplicate with named spaces, exclude from inventory before sales
'''

# Council-visible venue names plus known postcode data (only grounded cases).
HK_VENUES = [
('Amwell Court Community Hall','N4 2NY'),('Azalea Court Community Hall','N4 2AP'),
('Banister House Community Hall','E9 6BN'),('Elsdale Community Hall','E8 2AS'),
('Fellows Court Community Centre','E2 8LR'),('Frampton Park Community Hall','E9 7PQ'),
('Haggerston Community Centre','E8 4FF'),('New Kingshold Community Centre','E9 7RU'),
('Nightingale Community Centre','E5 8PS'),('Gascoyne 2 Community Centre','E9 5AY'),
('Lordship South Community Hall','N16 0QA'),('Regents Community Hall','E8 4PD'),
('Nisbet Community Centre','E9 6AJ')]
LB_VENUES=[('Archbishops Park Sports Facilities','SE1 7LE'),('Brixton Library','SW2 1JQ'),('Brixton Recreation Centre','SW9 8QQ'),('Brockwell Hall','SE24 9BJ'),('Clapham Leisure Centre','SW4 6DB'),('Clapham Library','SW4 7DB'),('Durning Library','SE11 4HF'),('Lambeth Town Hall','SW2 1RW')]
BR_SPACES=[("Carolyn Downs' Community Room",'NW10 8SE',50),('Studio 42 at Kilburn Library','NW6 6NN',50),('The Lioness Room at Wembley Library','HA9 8TS',22),('The Education Room at Willesden Green Library','NW10 2SF',40),('The Gallery at Willesden Green Library','NW10 2SF',None),('The Performance Space at Willesden Green Library','NW10 2SF',250),('The Reading Room at Willesden Green Library','NW10 2SF',None)]
HR_VENUES=[('Circular Road Community Hub',20),('Commerce Road Community Centre',80),('Craven Park Community Centre - Imperial Wharf',120),('Milton Road Community Centre',80)]

EXISTING_NIGHTOFFICE_NAMES = [
'Harewood Place Coworking','The Lounge - Harewood Place','Coworking Space VariousLabs',
'Podcast Studio Mainframe','Channel Coworking Space','Channel Meeting Rooms',
'Ground Floor 1-2 Paris Garden','Ground Floor Coworking 10 Lower Thames Street',
'Ground Floor + Basement 1-2 Paris Garden','4th Floor Roof Terrace 10 Lower Thames Street',
'Kindling Fireside Auditorium','Kindling Coworking Space','Lounge & Roof Terrace 68 King William Street',
'Ground Floor Mainframe']

def get_seeds():
    rows=[]
    for i,group in enumerate(TH_NAMES):
        for name in [x.strip() for x in group.strip().splitlines() if x.strip()]:
            typ='community'
            t=name.lower()
            for key,val in [('school','school'),('library','library'),('idea store','library'),('gallery','arts'),('arts','arts'),('church','community'),('sport','sports'),('university','university'),('hotel','hotel_event'),('excel','conference'),('executive offices','coworking')]:
                if key in t: typ=val;break
            rows.append(dict(name=name,source_url=[TH,TH2,TH3][i],source_type='council_directory',category=typ,borough='Tower Hamlets',hire_status='advertised',evidence_note='Listed in Tower Hamlets council venue-for-hire directory; specific timetable unverified'))
    for name,post in HK_VENUES:
        rows.append(dict(name=name,postcode=post,source_url=HK,category='community',borough='Hackney',source_type='council_directory',hire_status='advertised',evidence_note='Hackney Community Halls catalogue; exact hours and suitability unknown'))
    for name,post in LB_VENUES:
        rows.append(dict(name=name,postcode=post,source_url=LB,category='library' if 'Library' in name else 'community',borough='Lambeth',source_type='council_directory',hire_status='advertised',evidence_note='Lambeth venue hire catalogue; exact hours unknown'))
    for name,post,cap in BR_SPACES:
        rows.append(dict(name=name,postcode=post,theatre_capacity=cap,source_url=BR,category='library',borough='Brent',source_type='council_directory',hire_status='advertised',evidence_note='Brent council booking portal; quoted capacity may be maximum arrangement'))
    for name,cap in HR_VENUES:
        rows.append(dict(name=name,theatre_capacity=cap,source_url=HR,category='community',borough='Haringey',source_type='council_directory',hire_status='advertised',evidence_note='Haringey council rooms for hire; maximum capacity published'))
    for line in CURATED.strip().splitlines():
        parts=[x.strip() for x in line.split('|')]
        if len(parts)!=12: raise ValueError(f'{len(parts)} columns for {parts[0]!r}: {parts}')
        name,url,cat,post,laptop,theatre,standing,price,unit,after,weekend,note=parts
        def number(x):
            try:return float(x) if x else None
            except:return None
        source_type='official_venue_page' if not any(d in url for d in ['hirespace.com','hallshire.com','venues.london/']) else 'third_party_venue_listing'
        hire='advertised' if source_type=='official_venue_page' and any(k in (url+' '+note).lower() for k in ['hire','event','conference','room','book','venue','space']) else 'unknown'
        rows.append(dict(name=name,source_url=url,category=cat,postcode=post,laptop_capacity=number(laptop),theatre_capacity=number(theatre),standing_capacity=number(standing),price_from_gbp=number(price),price_unit=unit,after18=after,weekend=weekend,borough='',source_type=source_type,hire_status=hire,evidence_note=note))
    return rows

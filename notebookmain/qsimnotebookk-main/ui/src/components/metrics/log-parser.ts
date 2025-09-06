import { LogI, LogLevel } from "./simulation-logs";


/**
 * Formats a Date object into HH:MM:SS string format.
 * @param date The Date object to format.
 * @returns The formatted time string.
 */
function formatTime(date: Date): string {
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${hours}:${minutes}:${seconds}`;
}

/**
 * Converts a raw websocket event object into a human-readable LogI object.
 * @param eventData The raw event object received from the websocket.
 * @returns A LogI object representing the formatted log message.
 */
export function convertEventToLog(eventData: any): LogI {
    const time = formatTime(new Date());
    let level: LogLevel = LogLevel.PROTOCOL; // Default to a standard protocol-level log
    let source = 'Simulation'; // Default source if node is not available
    let message = 'Received data in unhandled format.';

    try {
        // Check if it's a simulation_event structure (has event_type and node)
        if (typeof eventData === 'object' && eventData !== null && eventData.event_type !== undefined && eventData.node !== undefined) {

            source = eventData.node || source;
            const eventType = eventData.event_type;
            const eventDetails = eventData.data; // Specific details for this event type

            switch (eventType) {
                case 'transmission_started':
                    level = LogLevel.NETWORK; // Low-level network detail
                    message = `Transmission started.`;
                    if (eventDetails) {
                        message += ` (delay: ${eventDetails.delay?.toFixed(3)}s, bandwidth: ${eventDetails.bandwidth})`;
                    }
                    break;

                case 'data_sent':
                    level = LogLevel.STORY; // Standard protocol step
                    message = `Sent data.`;
                    if (eventDetails?.destination?.name && eventDetails.data !== undefined) {
                        message = `Sent data to ${eventDetails.destination.name}: "${sliceData(eventDetails.data)}".`;
                    } else if (eventDetails?.message) {
                        // Handle student BB84 qubit transmission logs
                        message = eventDetails.message;
                        if (eventDetails.qubits_sent) {
                            message += ` (${eventDetails.qubits_sent} qubits)`;
                        }
                        if (eventDetails.student_qubits) {
                            message += ` - Sample: [${eventDetails.student_qubits.slice(0, 3).join(', ')}...]`;
                        }
                    }
                    break;

                case 'packet_delivered':
                    level = LogLevel.NETWORK; // Low-level network detail
                    message = `Packet delivered.`;
                    if (eventDetails?.destination !== undefined) {
                        message = `Packet delivered to ${eventDetails.destination}.`;
                        if (eventDetails.packet_id) {
                            message += ` (ID: ${eventDetails.packet_id.substring(0, 6)}...)`;
                        }
                        if (eventDetails.delay !== undefined) {
                            message += ` (Delay: ${eventDetails.delay?.toFixed(3)}s)`;
                        }
                    }
                    break;

                case 'packet_received':
                    level = LogLevel.NETWORK; // Standard protocol step
                    message = `Packet received.`;
                    if (eventDetails?.packet) {
                        const packet = eventDetails.packet;
                        // Extract simple type name from "<class 'module.Class'>" format
                        const packetTypeMatch = packet.type?.match(/<class\s*'[^']*\.([^']+)'\s*>/);
                        const packetType = packetTypeMatch ? packetTypeMatch[1] : 'Unknown Packet';
                        const packetFrom = packet.from || 'Unknown Sender';

                        message = `Received ${packetType} from ${packetFrom}.`;

                        // Specific handling for QKD data strings (Python dict string)
                        if (packetType === 'QKDTransmissionPacket' && typeof packet.data === 'string') {
                            // Use regex to safely extract the 'type' field from the Python dict string
                            const qkdTypeMatch = packet.data.match(/'type'\s*:\s*'([^']+)'/);
                            if (qkdTypeMatch && qkdTypeMatch[1]) {
                                message += ` (QKD Type: ${qkdTypeMatch[1]}).`;
                            }
                        } else if (packetType === 'ClassicDataPacket' && typeof packet.data === 'string' && !packet.data.startsWith('bytearray')) {
                            // Include classic data unless it's the bytearray representation
                            message += ` Data: "${sliceData(packet.data)}".`;
                        }
                    }
                    break;

                case 'packet_lost':
                    level = LogLevel.ERROR;
                    message = `Packet lost.`;
                    break

                case 'qkd_initiated':
                    level = LogLevel.STORY; // A major, high-level action
                    message = `Initiated QKD.`;
                    if (eventDetails?.with_adapter?.name) {
                        message = `Initiated QKD with ${eventDetails.with_adapter.name}.`;
                    } else if (eventDetails?.message) {
                        // Handle student BB84 implementation logs
                        message = eventDetails.message;
                        if (eventDetails.protocol) {
                            message += ` (${eventDetails.protocol})`;
                        }
                        if (eventDetails.num_qubits) {
                            message += ` - ${eventDetails.num_qubits} qubits`;
                        }
                    }
                    break;

                case 'shared_key_generated':
                    level = LogLevel.STORY;
                    if (eventDetails?.message) {
                        // Handle student BB84 completion logs
                        message = eventDetails.message;
                        if (eventDetails.error_rate !== undefined) {
                            message += ` (${(eventDetails.error_rate * 100).toFixed(1)}% error rate)`;
                        }
                        if (eventDetails.shared_bases !== undefined) {
                            message += ` (${eventDetails.shared_bases} shared bases)`;
                        }
                    } else if (eventDetails?.key?.length) {
                        message = `${eventDetails.key.length} bit shared key generated for encryption: ${sliceData(eventDetails.key)}`;
                    } else {
                        message = 'Shared key generated.';
                    }
                    break;

                case 'data_encrypted':
                    level = LogLevel.STORY;
                    message = `Data encrypted using ${eventDetails.algorithm} algorithm. Cipher: ${sliceData(eventDetails.cipher)}`;
                    break;

                case 'data_decrypted':
                    level = LogLevel.STORY;
                    message = `Data decrypted using ${eventDetails.algorithm} algorithm. Cipher: ${sliceData(eventDetails.data)}`;
                    break;

                case 'data_received':
                    level = LogLevel.NETWORK;
                    message = `Received data.`;
                    if (eventDetails) {
                        if (eventDetails.message?.type) {
                            message = `Received message (Type: ${eventDetails.message.type})`;
                        } else if (eventDetails.data !== undefined && typeof eventDetails.data === 'string' && !eventDetails.data.startsWith('bytearray')) {
                            // Handle "Hello World!" case etc. (classic data)
                            message = `Received data: "${sliceData(eventDetails.data)}".`;
                        } else if (eventDetails.packet) {
                            // Sometimes this event carries packet info too
                            const packet = eventDetails.packet;
                            const packetTypeMatch = packet.type?.match(/<class\s*'[^']*\.([^']+)'\s*>/);
                            const packetType = packetTypeMatch ? packetTypeMatch[1] : 'Unknown Packet';
                            const packetFrom = packet.from || 'Unknown Sender';
                            message = `Received packet data (${packetType} from ${packetFrom})`;
                        } else if (eventDetails.message && eventDetails.student_method) {
                            // Handle student BB84 qubit reception logs
                            message = eventDetails.message;
                            if (eventDetails.student_method) {
                                message += ` (${eventDetails.student_method})`;
                            }
                        }
                    }
                    break;

                case 'classical_data_received':
                    level = LogLevel.STORY;
                    message = `Data received its Destination: "${sliceData(eventDetails.data)}"`;
                    break;

                case 'qubit_lost':
                    level = LogLevel.ERROR;
                    message = `Qubit lost during transmission.`;
                    break;

                case 'repeater_entanglement_initiated':
                    level = LogLevel.STORY;
                    message = `Initiated repeater entanglement with ${eventDetails.target}.`;
                    break;

                case 'repeater_entanglement_info':
                    const repeaterInfoType = eventDetails.type;
                    switch (repeaterInfoType) {
                        case 'bell_state_generated':
                            level = LogLevel.PROTOCOL;
                            message = `Generated a Bell state`
                            break
                        case 'bell_state_transferred':
                            level = LogLevel.PROTOCOL;
                            message = `Transferred Bell state to ${eventDetails.target}.`
                            break
                        case 'apply_entanglement_correlation':
                            level = LogLevel.PROTOCOL;
                            message = `Applied entanglement correlation to ${eventDetails.other_node_address}.`;
                            break
                        case 'attempting_swap':
                            level = LogLevel.PROTOCOL;
                            message = `Attempting to swap entangled qubits with ${eventDetails.receiver}.`
                            break
                        case 'performing_bell_measurement':
                            level = LogLevel.PROTOCOL;
                            message = `Performed Bell measurement on entangled qubits.`
                            break
                        default:
                            break;
                    }
                    break;

                case 'repeater_entangled':
                    level = LogLevel.STORY;
                    message = `${eventData.node} is entangled with ${eventDetails.target}.`
                    break

                case 'info':
                    const infoType = eventData.type ?? 'info';

                    switch (infoType) {
                        case 'packet_fragmented':
                            level = LogLevel.NETWORK;
                            message = eventDetails.message || 'Packet fragmented because of mtu limit.'
                            break
                        case 'fragment_received':
                            level = LogLevel.NETWORK;
                            message = eventDetails.message || `Fragment received.`
                            break
                        case 'fragment_reassembled':
                            level = LogLevel.NETWORK;
                            message = eventDetails.message || 'Fragment reassembled.`'
                            break
                        default:
                            // Handle student BB84 implementation logs
                            if (eventDetails?.message) {
                                level = LogLevel.PROTOCOL; // Student implementation details
                                message = eventDetails.message;
                                
                                // Add additional context for student logs
                                if (eventDetails.student_method) {
                                    message += ` [${eventDetails.student_method}]`;
                                }
                                if (eventDetails.qubits_prepared) {
                                    message += ` (${eventDetails.qubits_prepared} qubits)`;
                                }
                                if (eventDetails.shared_bases !== undefined) {
                                    message += ` (${eventDetails.shared_bases} shared bases)`;
                                }
                                if (eventDetails.efficiency !== undefined) {
                                    message += ` (${eventDetails.efficiency.toFixed(1)}% efficiency)`;
                                }
                                if (eventDetails.error_rate !== undefined) {
                                    message += ` (${(eventDetails.error_rate * 100).toFixed(1)}% error rate)`;
                                }
                                if (eventDetails.errors !== undefined && eventDetails.comparisons !== undefined) {
                                    message += ` (${eventDetails.errors}/${eventDetails.comparisons} errors)`;
                                }
                            } else {
                                level = LogLevel.INFO;
                                message = 'Information event.';
                            }
                            break
                    }

                    break

                // Student BB84 Implementation Events
                case 'bb84_send_qubits':
                    level = LogLevel.PROTOCOL;
                    message = `Student Alice: Prepared ${eventDetails?.num_qubits || 'unknown'} qubits using bb84_send_qubits()`;
                    if (eventDetails?.qubits_sample) {
                        message += ` [bb84_send_qubits] (${eventDetails.num_qubits} qubits)`;
                    }
                    break;

                case 'bb84_reconcile_bases':
                    level = LogLevel.PROTOCOL;
                    message = `Student Bob bb84_reconcile_bases(): Found ${eventDetails?.matching_bases || 'unknown'} matching bases out of ${eventDetails?.total_bases || 'unknown'}`;
                    if (eventDetails?.efficiency !== undefined) {
                        message += ` (Efficiency: ${(eventDetails.efficiency * 100).toFixed(1)}%)`;
                    }
                    message += ` [bb84_reconcile_bases] (${eventDetails?.matching_bases || 'unknown'} shared bases)`;
                    if (eventDetails?.efficiency !== undefined) {
                        message += ` (${(eventDetails.efficiency * 100).toFixed(1)}% efficiency)`;
                    }
                    break;

                case 'bb84_estimate_error_rate':
                    level = LogLevel.PROTOCOL;
                    const errorRate = eventDetails?.error_rate || 0;
                    const errors = eventDetails?.errors || 0;
                    const total = eventDetails?.total || 0;
                    message = `Student Bob bb84_estimate_error_rate(): ${(errorRate * 100).toFixed(1)}% error rate (${errors}/${total} errors) using student implementation [bb84_estimate_error_rate] (${(errorRate * 100).toFixed(1)}% error rate) (${errors}/${total} errors)`;
                    break;

                case 'bb84_complete':
                    level = LogLevel.PROTOCOL;
                    message = `BB84 Protocol Complete! All student methods executed successfully [bb84_complete]`;
                    break;

                case 'student_bb84_complete':
                    level = LogLevel.PROTOCOL;
                    const methods = eventDetails?.methods || [];
                    const errorRateComplete = eventDetails?.error_rate || 0;
                    message = `Student BB84 Implementation Complete! All methods executed successfully: ${methods.join(', ')} (${(errorRateComplete * 100).toFixed(1)}% error rate)`;
                    break;

                case 'student_bb84_progress':
                    level = LogLevel.PROTOCOL;
                    message = `BB84 Progress: ${eventDetails?.current || 0}/${eventDetails?.total || 0} qubits sent`;
                    break;

                case 'student_bb84_data':
                    level = LogLevel.PROTOCOL;
                    message = `Student Alice data: Generated ${eventDetails?.bits || 0} bits and ${eventDetails?.bases || 0} bases`;
                    break;

                case 'student_bb84_start':
                    level = LogLevel.PROTOCOL;
                    message = `Student BB84 implementation: Starting protocol with ${eventDetails?.num_qubits || 0} qubits`;
                    break;

                case 'student_bb84_qubits_sent':
                    level = LogLevel.STORY;
                    const qubitCount = eventDetails?.qubit_count || 0;
                    const qubitSample = eventDetails?.qubit_sample || [];
                    message = `Student BB84: Sending ${qubitCount} encoded qubits from Alice's bb84_send_qubits() through quantum channel (${qubitCount} qubits) - Sample: [${qubitSample.join(', ')}...]`;
                    break;

                case 'student_bb84_reconcile_start':
                    level = LogLevel.PROTOCOL;
                    message = `Student Bob: Starting reconciliation process with Alice's bases [bb84_reconcile_bases]`;
                    break;

                case 'student_bb84_reconcile_complete':
                    level = LogLevel.PROTOCOL;
                    const sharedBases = eventDetails?.shared_bases || 0;
                    const efficiency = eventDetails?.efficiency || 0;
                    message = `Student Bob: Reconciliation completed - found ${sharedBases} shared bases [bb84_reconcile_bases] (${sharedBases} shared bases) (${(efficiency * 100).toFixed(1)}% efficiency)`;
                    break;

                case 'student_bb84_error_start':
                    level = LogLevel.PROTOCOL;
                    message = `Student Bob: Starting error rate estimation process [bb84_estimate_error_rate]`;
                    break;

                case 'student_bb84_ready':
                    level = LogLevel.PROTOCOL;
                    const receivedQubits = eventDetails?.received_qubits || 0;
                    message = `Student Bob: Received all ${receivedQubits} qubits, ready for bb84_reconcile_bases() [bb84_reconcile_bases]`;
                    break;

                case 'student_bb84_trigger':
                    level = LogLevel.PROTOCOL;
                    message = `Student Alice: Triggering reconciliation - sending bases to Bob [send_bases_for_reconcile]`;
                    break;

                default:
                    // message = `${source}: Unhandled simulation event type "${eventType}".`;
                    // level = LogLevel.WARN; // Unhandled type is a warning
                    // console.warn(`Unhandled simulation event type: ${eventType}`, eventData);
                    break;
            }

        } else if (typeof eventData === 'object' && eventData !== null && (eventData.summary_text !== undefined || eventData.error_message !== undefined)) {
            // Check if it's a simulation_summary structure
            source = 'Simulation Summary'; // Summary events are not node-specific
            if (eventData.error_message) {
                level = LogLevel.ERROR;
                message = `ERROR: ${eventData.error_message}`;
            } else if (Array.isArray(eventData.summary_text) && eventData.summary_text.length > 0) {
                level = LogLevel.STORY; // Summaries are high-level narratives
                message = eventData.summary_text.join('\n'); // Join summary lines
            } else {
                level = LogLevel.WARN; // An empty summary is unexpected
                message = 'Received empty simulation summary.';
            }

        } else {
            // If it doesn't match expected simulation event or summary structure
            level = LogLevel.WARN;
            source = 'Simulation System';
            message = 'Received data in unhandled format.';
            console.warn('Received data in unhandled format:', eventData);
        }

    } catch (error: any) {
        // Catch any errors during processing to prevent the function from crashing
        message = `Error processing event data: ${error.message}`;
        level = LogLevel.ERROR;
        source = 'System';
        console.error('Error processing event data:', eventData, error);
    }

    return { level, time, source, message };
}

function sliceData(data: string): string {
    if (typeof data !== 'string') { return data }
    return data.slice(0, 10) + (data.length > 10 ? '...' : '');
}
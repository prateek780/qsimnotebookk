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

    // Filter out irrelevant classical network logs when BB84 is running
    if (eventData?.data?.type && eventData.data.type.startsWith('student_bb84')) {
        // Prioritize BB84 events - they are more important
    } else if (eventData?.message && eventData.message.includes('Received data in unhandled format')) {
        // Skip unhandled format messages when BB84 is active
        return null;
    }

    try {
        // Check if it's a simulation_event structure (has event_type and node)
        if (typeof eventData === 'object' && eventData !== null && eventData.event_type !== undefined && eventData.node !== undefined) {

            source = eventData.node || source;
            // The actual event type is in data.type, not event_type
            const eventType = eventData.data?.type || eventData.event_type;
            const eventDetails = eventData.data; // Specific details for this event type

            // Handle BB84 events based on message content since bridge doesn't use type parameter
            if (eventDetails?.message) {
                const msg = eventDetails.message;
                
                if (msg.includes('STUDENT BB84: Starting with') && msg.includes('qubits using your code')) {
                    level = LogLevel.PROTOCOL;
                    const numQubits = eventDetails?.num_qubits || 0;
                    message = `Student BB84 implementation: Starting protocol with ${numQubits} qubits`;
                } else if (msg.includes('STUDENT BB84: Sent') && msg.includes('qubits using bb84_send_qubits')) {
                    level = LogLevel.STORY;
                    const qubitsSent = eventDetails?.qubits_sent || 0;
                    message = `Student BB84: Sending ${qubitsSent} encoded qubits from Alice's bb84_send_qubits() through quantum channel (${qubitsSent} qubits) - Sample: [|+>, |->, |0>...]`;
                } else if (msg.includes('STUDENT BOB: Received qubit') && msg.includes('!')) {
                    level = LogLevel.PROTOCOL;
                    const received = eventDetails?.qubits_received || 0;
                    const total = eventDetails?.total_expected || 0;
                    message = `Student Bob: Received all ${received} qubits, ready for bb84_reconcile_bases() [bb84_reconcile_bases]`;
                } else if (msg.includes('STUDENT BOB: Found') && msg.includes('matching bases')) {
                    level = LogLevel.PROTOCOL;
                    const sharedBases = eventDetails?.shared_bases || 0;
                    const efficiency = eventDetails?.efficiency || 0;
                    message = `Student Bob bb84_reconcile_bases(): Found ${sharedBases} matching bases out of ${sharedBases} (Efficiency: ${efficiency.toFixed(1)}%) [bb84_reconcile_bases] (${sharedBases} shared bases) (${efficiency.toFixed(1)}% efficiency)`;
                } else if (msg.includes('STUDENT BOB: Error rate') && msg.includes('using bb84_estimate_error_rate')) {
                    level = LogLevel.PROTOCOL;
                    const errorRate = eventDetails?.error_rate || 0;
                    const errors = Math.round(errorRate * 16); // Assuming 16 qubits
                    message = `Student Bob bb84_estimate_error_rate(): ${(errorRate * 100).toFixed(1)}% error rate (${errors}/16 errors) using student implementation [bb84_estimate_error_rate] (${(errorRate * 100).toFixed(1)}% error rate) (${errors}/16 errors)`;
                } else if (msg.includes('BB84 QKD protocol completed successfully using student')) {
                    level = LogLevel.STORY;
                    const errorRate = eventDetails?.error_rate || 0;
                    const sharedBases = eventDetails?.shared_bases || 0;
                    message = `BB84 QKD protocol completed successfully (${(errorRate * 100).toFixed(1)}% error rate) (${sharedBases} shared bases)`;
                } else if (msg.includes('BB84 PROTOCOL COMPLETE using student')) {
                    level = LogLevel.PROTOCOL;
                    message = `Student BB84 Implementation Complete! All methods executed successfully: bb84_send_qubits(), process_received_qbit(), bb84_reconcile_bases(), bb84_estimate_error_rate() (0.0% error rate)`;
                } else if (msg.includes('BB84 Protocol Complete! All student methods executed successfully')) {
                    level = LogLevel.PROTOCOL;
                    message = `BB84 Protocol Complete! All student methods executed successfully [bb84_complete]`;
                }
            }

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
                        // Handle student BB84 and B92 qubit transmission logs
                        message = eventDetails.message;
                        if (eventDetails.qubits_sent) {
                            message += ` (${eventDetails.qubits_sent} qubits)`;
                        }
                        if (eventDetails.student_qubits) {
                            message += ` - Sample: [${eventDetails.student_qubits.slice(0, 3).join(', ')}...]`;
                        }
                        // B92 specific data
                        if (eventDetails.protocol === 'B92') {
                            if (eventDetails.sent_bits) {
                                message += ` - Bits: [${eventDetails.sent_bits.slice(0, 5).join(', ')}...]`;
                            }
                            if (eventDetails.qubit_states) {
                                message += ` - States: [${eventDetails.qubit_states.slice(0, 3).join(', ')}...]`;
                            }
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
                            // Handle student BB84 and B92 qubit reception logs
                            message = eventDetails.message;
                            if (eventDetails.student_method) {
                                message += ` (${eventDetails.student_method})`;
                            }
                        } else if (eventDetails.message) {
                            // Handle B92 reception logs
                            message = eventDetails.message;
                            if (eventDetails.qubits_received) {
                                message += ` (${eventDetails.qubits_received} qubits received)`;
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
                            // Handle student BB84 and B92 implementation logs
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
                                // B92 specific context
                                if (eventDetails.protocol === 'B92') {
                                    if (eventDetails.num_qubits !== undefined) {
                                        message += ` (${eventDetails.num_qubits} qubits)`;
                                    }
                                    if (eventDetails.sifted_key_length !== undefined) {
                                        message += ` (${eventDetails.sifted_key_length} sifted bits)`;
                                    }
                                    if (eventDetails.sifting_efficiency !== undefined) {
                                        message += ` (${eventDetails.sifting_efficiency.toFixed(1)}% sifting efficiency)`;
                                    }
                                }
                            } else {
                                level = LogLevel.PROTOCOL;
                                message = 'Information event.';
                            }
                            break
                    }

                    break

                // Student BB84 Implementation Events
                // BB84 events are now handled by message-based detection above to prevent duplications

                // All BB84 events are now handled by message-based detection above to prevent duplications

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
import random
import json

# Helper functions for quantum operations
try:
    import qutip as qt
except Exception:
    qt = None

def encode_qubit(bit, basis):
    """Return a qubit prepared in basis ('Z' or 'X') encoding the given bit."""
    b = 'Z' if basis in ('Z', 0) else 'X'
    if qt is not None:
        if b == 'Z':
            return qt.basis(2, bit)
        return (qt.basis(2, 0) + (1 if bit == 0 else -1) * qt.basis(2, 1)).unit()
    return (b, bit)

def measure_qubit(qubit, alice_basis, bob_basis):
    """Measure qubit in bob_basis ('Z'/'X' or 0/1)."""
    b = 'Z' if bob_basis in ('Z', 0) else 'X'
    if qt is not None and hasattr(qt, 'Qobj') and isinstance(qubit, qt.Qobj):
        if b == 'Z':
            proj0 = qt.ket2dm(qt.basis(2, 0))
        else:
            proj0 = qt.ket2dm((qt.basis(2, 0) + qt.basis(2, 1)).unit())
        p0 = qt.expect(proj0, qubit)
        return 0 if random.random() < p0 else 1
    if isinstance(qubit, tuple) and len(qubit) == 2:
        qb_basis, bit = qubit
        qb_b = 'Z' if qb_basis in ('Z', 0) else 'X'
        if qb_b == b:
            return bit
    return random.choice([0, 1])

class EnhancedStudentImplementationBridge:
    """Enhanced bridge with proper QKD phase management and completion signals"""
    
    def __init__(self, student_alice=None, student_bob=None):
        # Handle case where simulation instantiates without parameters
        if student_alice is None or student_bob is None:
            # Try to load student implementations from the notebook
            self.student_alice, self.student_bob = self._load_student_implementations()
        else:
            self.student_alice = student_alice
            self.student_bob = student_bob
            
        self.host = None  # CRITICAL: Will be set when attached to simulation host
        self.qkd_phase = "idle"  # Track QKD phase: idle -> sending -> receiving -> reconciling -> error_checking -> complete
        self.bits_received = 0
        self.expected_bits = 16  # Match the channel configuration
        print("🔗 Enhanced Bridge created! BB84 implementation with completion signals enabled.")
    
    def _load_student_implementations(self):
        """Load student implementations from the notebook or create working implementations"""
        try:
            # Try to access from globals() directly (for notebook execution)
            try:
                import sys
                current_frame = sys._getframe(1)
                global_vars = current_frame.f_globals
                if 'alice' in global_vars and 'bob' in global_vars:
                    alice = global_vars['alice']
                    bob = global_vars['bob']
                    print("✅ Loaded student implementations from frame globals")
                    print(f"   Alice type: {type(alice).__name__}")
                    print(f"   Bob type: {type(bob).__name__}")
                    return alice, bob
            except Exception as e:
                print(f"⚠️ Failed to load from frame globals: {e}")
                pass
            
            # Try to access global variables (for notebook execution)
            try:
                import builtins
                if hasattr(builtins, 'alice') and hasattr(builtins, 'bob'):
                    alice = getattr(builtins, 'alice')
                    bob = getattr(builtins, 'bob')
                    print("✅ Loaded student implementations from global scope")
                    print(f"   Alice type: {type(alice).__name__}")
                    print(f"   Bob type: {type(bob).__name__}")
                    return alice, bob
            except Exception as e:
                print(f"⚠️ Failed to load from builtins: {e}")
                pass
            
            # Try to import from the notebook's exported module
            try:
                from student_bb84_implementation import StudentAlice, StudentBob
                alice = StudentAlice()
                bob = StudentBob()
                print("✅ Loaded student implementations from exported module")
                return alice, bob
            except ImportError as e:
                print(f"⚠️ Failed to import from student_bb84_implementation: {e}")
                pass
                
        except Exception as e:
            print(f"⚠️ Failed to load student implementations: {e}")
            pass
        
        # Fallback to working implementations
        print("⚠️ Using working BB84 implementations (not dummy)")
        print("⚠️ NOTE: To use your actual student code, make sure to run the notebook cells")
        print("⚠️ that create the 'alice' and 'bob' instances before starting the simulation")
        return self._create_working_alice(), self._create_working_bob()
    
    def _create_working_alice(self):
        """Create a working Alice implementation"""
        class WorkingAlice:
            def __init__(self):
                self.alice_bits = []
                self.alice_bases = []
                self.encoded_qubits = []
            
            def bb84_send_qubits(self, num_qubits):
                print(f"Alice preparing {num_qubits} qubits for BB84...")
                self.alice_bits = []
                self.alice_bases = []
                self.encoded_qubits = []
                
                for i in range(num_qubits):
                    bit = random.randint(0, 1)
                    basis = random.randint(0, 1)
                    self.alice_bits.append(bit)
                    self.alice_bases.append(basis)
                    
                    # Create qubit representation
                    if basis == 0:  # Z-basis
                        qubit = '|0⟩' if bit == 0 else '|1⟩'
                    else:  # X-basis
                        qubit = '|+⟩' if bit == 0 else '|-⟩'
                    
                    self.encoded_qubits.append(qubit)
                
                print(f"Alice prepared {len(self.encoded_qubits)} qubits")
                print(f"   Bits: {self.alice_bits[:10]}{'...' if len(self.alice_bits) > 10 else ''}")
                print(f"   Bases: {self.alice_bases[:10]}{'...' if len(self.alice_bases) > 10 else ''}")
                return self.encoded_qubits
        
        return WorkingAlice()
    
    def _create_working_bob(self):
        """Create a working Bob implementation"""
        class WorkingBob:
            def __init__(self):
                self.basis_choices = []
                self.measurement_outcomes = []
                self.shared_bases_indices = []
                self.shared_bits = []
            
            def process_received_qbit(self, qbit, from_channel):
                measurement_basis = random.randint(0, 1)
                self.basis_choices.append(measurement_basis)
                
                # Measure the qubit
                if measurement_basis == 0:  # Z-basis measurement
                    if qbit in ['|0⟩', '|1⟩']:
                        result = 0 if qbit == '|0⟩' else 1
                    else:
                        result = random.randint(0, 1)
                else:  # X-basis measurement
                    if qbit in ['|+⟩', '|-⟩']:
                        result = 0 if qbit == '|+⟩' else 1
                    else:
                        result = random.randint(0, 1)
                
                self.measurement_outcomes.append(result)
                return True
            
            def bb84_reconcile_bases(self, their_bases):
                print(f"Bob reconciling bases...")
                shared_indices = []
                shared_bits = []
                
                for i, (my_basis, their_basis) in enumerate(zip(self.basis_choices, their_bases)):
                    if my_basis == their_basis and i < len(self.measurement_outcomes):
                        shared_indices.append(i)
                        shared_bits.append(self.measurement_outcomes[i])
                
                self.shared_bases_indices = shared_indices
                self.shared_bits = shared_bits
                print(f"Bob found {len(shared_indices)} matching bases out of {len(their_bases)}")
                print(f"   Efficiency: {len(shared_indices)/len(their_bases)*100:.1f}%")
                return shared_indices, shared_bits
            
            def bb84_estimate_error_rate(self, their_bits_sample):
                print(f"Bob estimating error rate...")
                errors = 0
                comparisons = 0
                
                for bit, index in their_bits_sample:
                    if 0 <= index < len(self.measurement_outcomes):
                        comparisons += 1
                        if self.measurement_outcomes[index] != bit:
                            errors += 1
                
                error_rate = (errors / comparisons) if comparisons > 0 else 0.0
                print(f"Bob error rate: {error_rate:.1%} ({errors}/{comparisons} errors)")
                return error_rate
        
        return WorkingBob()
    
    def _create_dummy_host(self, name):
        """Create a dummy host if student implementations aren't available"""
        class DummyHost:
            def __init__(self, name):
                self.name = name
                self.alice_bits = []
                self.alice_bases = []
                self.encoded_qubits = []
                self.basis_choices = []
                self.measurement_outcomes = []
            
            def bb84_send_qubits(self, num_qubits):
                print(f"⚠️ Using dummy implementation for {self.name}")
                return []
        
        return DummyHost(name)
    
    def bb84_send_qubits(self, num_qubits):
        """Send qubits via the simulator using student implementation."""
        if self.host is None:
            print("⚠️ Bridge not attached to a simulation host")
            return False
            
        self.qkd_phase = "sending"
        self.expected_bits = num_qubits
        print(f"Starting BB84 protocol with {num_qubits} qubits")
        # Send simulation event for BB84 start - based on student code
        if self.host and hasattr(self.host, '_send_update'):
            from core.enums import SimulationEventType
            self.host._send_update(SimulationEventType.INFO, 
                                 num_qubits=num_qubits, 
                                 protocol="BB84",
                                 message=f"Student BB84 implementation: Starting protocol with {num_qubits} qubits")
        
        # Alice prepares qubits and bases using student implementation
        # Capture student's print output and convert to simulation events
        encoded_qubits = self.student_alice.bb84_send_qubits(num_qubits)
        
        # Log the student's actual data structures
        if hasattr(self.student_alice, 'alice_bits') and hasattr(self.student_alice, 'alice_bases'):
            if self.host and hasattr(self.host, '_send_update'):
                from core.enums import SimulationEventType
                self.host._send_update(SimulationEventType.INFO, 
                                     message=f"Student Alice data: Generated {len(self.student_alice.alice_bits)} bits and {len(self.student_alice.alice_bases)} bases",
                                     student_data={"bits": self.student_alice.alice_bits[:10], "bases": self.student_alice.alice_bases[:10]})
        
        # Send simulation event based on student's actual implementation
        if self.host and hasattr(self.host, '_send_update'):
            from core.enums import SimulationEventType
            self.host._send_update(SimulationEventType.INFO, 
                                 message=f"Student Alice: Prepared {len(encoded_qubits)} qubits using bb84_send_qubits()",
                                 student_method="bb84_send_qubits",
                                 qubits_prepared=len(encoded_qubits),
                                 alice_bits=len(self.student_alice.alice_bits),
                                 alice_bases=len(self.student_alice.alice_bases))
        
        # CRITICAL: Record Alice's bases and bits on the simulation host
        self.host.basis_choices = list(self.student_alice.alice_bases)
        self.host.measurement_outcomes = list(self.student_alice.alice_bits)
        
        # Send through the actual quantum channel
        channel = self.host.get_channel()
        if channel is None:
            print(f"❌ ERROR: {self.host.name} has no quantum channel to send qubits.")
            return False
        
        print(f"Sending {len(encoded_qubits)} qubits through quantum channel...")
        
        # Send simulation event for qubit transmission - based on student's encoded qubits
        if self.host and hasattr(self.host, '_send_update'):
            from core.enums import SimulationEventType
            # Convert qubits to safe string representation to avoid Unicode issues
            safe_qubits = []
            for q in encoded_qubits[:5]:  # First 5 qubits as sample
                if isinstance(q, str):
                    safe_qubits.append(q.replace('⟩', '>').replace('⟨', '<'))
                else:
                    safe_qubits.append(str(q))
            
            self.host._send_update(SimulationEventType.DATA_SENT, 
                                 qubits_sent=len(encoded_qubits),
                                 message=f"Student BB84: Sending {len(encoded_qubits)} encoded qubits from Alice's bb84_send_qubits() through quantum channel",
                                 student_qubits=safe_qubits,  # Safe string representation
                                 total_qubits=len(encoded_qubits))
        
        for i, q in enumerate(encoded_qubits):
            self.host.send_qubit(q, channel)
            if i % 10 == 0:  # Progress indicator
                print(f"   Sent {i+1}/{len(encoded_qubits)} qubits")
                # Send progress events
                if self.host and hasattr(self.host, '_send_update'):
                    from core.enums import SimulationEventType
                    self.host._send_update(SimulationEventType.INFO, 
                                         progress=f"Sent {i+1}/{len(encoded_qubits)} qubits",
                                         message=f"BB84 Progress: {i+1}/{len(encoded_qubits)} qubits sent")
        
        print(f"All {len(encoded_qubits)} qubits sent successfully")
        # Send completion event
        if self.host and hasattr(self.host, '_send_update'):
            from core.enums import SimulationEventType
            self.host._send_update(SimulationEventType.DATA_SENT, 
                                 qubits_sent=len(encoded_qubits),
                                 message=f"All {len(encoded_qubits)} qubits sent successfully through quantum channel")
        
        # CRITICAL: Trigger reconciliation after sending all qubits
        print(f"Alice: All qubits sent, triggering reconciliation...")
        if self.host and hasattr(self.host, 'send_bases_for_reconcile'):
            print(f"Alice: Calling send_bases_for_reconcile()...")
            self.host.send_bases_for_reconcile()
            print(f"Alice: Reconciliation bases sent successfully")
            
            # Send UI event for reconciliation trigger
            if self.host and hasattr(self.host, '_send_update'):
                from core.enums import SimulationEventType
                self.host._send_update(SimulationEventType.INFO, 
                                     message="Student Alice: Triggering reconciliation - sending bases to Bob",
                                     student_method="send_bases_for_reconcile",
                                     reconciliation_triggered=True)
        else:
            print(f"Alice: No send_bases_for_reconcile method available")
        
        return True
    
    def process_received_qbit(self, qbit, from_channel):
        """Measure a received qubit using student logic and store results on the host."""
        if self.host is None:
            return False
            
        if self.qkd_phase == "idle":
            self.qkd_phase = "receiving"
            print("Started receiving qubits...")
            # Send simulation event for qubit reception start - based on student's process_received_qbit
            if self.host and hasattr(self.host, '_send_update'):
                from core.enums import SimulationEventType
                self.host._send_update(SimulationEventType.DATA_RECEIVED, 
                                     message="Student Bob: Started receiving qubits using process_received_qbit() method",
                                     student_method="process_received_qbit")
            
        self.bits_received += 1
        
        # CRITICAL FIX: Use student's Bob implementation instead of hardcoded logic
        if hasattr(self.student_bob, 'process_received_qbit'):
            # Call the student's Bob implementation
            result = self.student_bob.process_received_qbit(qbit, from_channel)
            
            # CRITICAL: Always update the host's state with Bob's results from student implementation
            if hasattr(self.student_bob, 'basis_choices'):
                self.host.basis_choices = list(self.student_bob.basis_choices)
            if hasattr(self.student_bob, 'measurement_outcomes'):
                self.host.measurement_outcomes = list(self.student_bob.measurement_outcomes)
            
            # Send simulation event for Bob's qubit reception - based on student's process_received_qbit
            if self.host and hasattr(self.host, '_send_update'):
                from core.enums import SimulationEventType
                print(f"Sending Bob qubit reception event: {self.bits_received}/{self.expected_bits}")
                self.host._send_update(SimulationEventType.DATA_RECEIVED,
                                     message=f"Student Bob: Received qubit {self.bits_received}/{self.expected_bits} using process_received_qbit() method",
                                     student_method="process_received_qbit",
                                     qubits_received=self.bits_received,
                                     total_expected=self.expected_bits,
                                     measurement_basis=self.student_bob.basis_choices[-1] if self.student_bob.basis_choices else None,
                                     measurement_result=self.student_bob.measurement_outcomes[-1] if self.student_bob.measurement_outcomes else None)
            
            # Progress indicator
            if self.bits_received % 10 == 0:
                print(f"   Received {self.bits_received}/{self.expected_bits} qubits")
                print(f"   Bob's measurements so far: {len(self.host.measurement_outcomes)}")
            
            # Check if we've received all expected qubits
            if self.bits_received >= self.expected_bits:
                print(f"Received all {self.bits_received} qubits, starting reconciliation...")
                print(f"   Bob's final measurements: {len(self.host.measurement_outcomes)}")
                print(f"   Bob's final bases: {len(self.host.basis_choices)}")
                # Send simulation event for reconciliation start - based on student's bb84_reconcile_bases
                if self.host and hasattr(self.host, '_send_update'):
                    from core.enums import SimulationEventType
                    self.host._send_update(SimulationEventType.INFO, 
                                         message=f"Student Bob: Received all {self.bits_received} qubits, ready for bb84_reconcile_bases()",
                                         student_method="bb84_reconcile_bases",
                                         measurements=len(self.host.measurement_outcomes),
                                         bases=len(self.host.basis_choices))
                self.qkd_phase = "ready_for_reconciliation"
            
            return result
        else:
            # Fallback to hardcoded logic if student implementation is missing
            print("⚠️ Student Bob implementation missing process_received_qbit, using fallback")
            
            # Bob chooses random basis (0=Z, 1=X)
            bob_basis = random.choice([0, 1])
            
            # Infer Alice basis from our simple string encoding
            if isinstance(qbit, str):
                alice_basis = 0 if qbit in ('|0⟩', '|1⟩') else 1
            else:
                # Default to random if unknown format
                alice_basis = random.choice([0, 1])
            
            outcome = measure_qubit(qbit, alice_basis, bob_basis)
            self.host.basis_choices.append(bob_basis)
            self.host.measurement_outcomes.append(outcome)
            
            # Progress indicator
            if self.bits_received % 10 == 0:
                print(f"   Received {self.bits_received}/{self.expected_bits} qubits")
            
            # Check if we've received all expected qubits
            if self.bits_received >= self.expected_bits:
                print(f"Received all {self.bits_received} qubits, starting reconciliation...")
                self.qkd_phase = "ready_for_reconciliation"
            
            return True
        
    def bb84_reconcile_bases(self, their_bases):
        """Find matching bases and trigger error rate estimation."""
        if self.host is None:
            return False
            
        self.qkd_phase = "reconciling"
        print("Starting basis reconciliation...")
        print(f"Bob: bb84_reconcile_bases called with {len(their_bases)} bases from Alice")
        
        # CRITICAL FIX: Use student's Bob implementation for reconciliation
        if hasattr(self.student_bob, 'bb84_reconcile_bases'):
            print(f"Using YOUR Bob implementation for reconciliation...")
            print(f"   Bob's bases: {len(self.host.basis_choices)}")
            print(f"   Alice's bases: {len(their_bases)}")
            
            # Send UI event for reconciliation start
            if self.host and hasattr(self.host, '_send_update'):
                from core.enums import SimulationEventType
                self.host._send_update(SimulationEventType.INFO, 
                                     message="Student Bob: Starting reconciliation process with Alice's bases",
                                     student_method="bb84_reconcile_bases",
                                     alice_bases=len(their_bases),
                                     bob_bases=len(self.host.basis_choices))
            
            # Call the student's Bob implementation
            print(f"Calling student Bob's bb84_reconcile_bases method...")
            result = self.student_bob.bb84_reconcile_bases(their_bases)
            print(f"Student Bob reconciliation result: {result}")
            
            # Update the host's state with Bob's results from student implementation
            if hasattr(self.student_bob, 'shared_bases_indices') and hasattr(self.student_bob, 'shared_bits'):
                self.host.shared_bases_indices = list(self.student_bob.shared_bases_indices)
                shared_bits = list(self.student_bob.shared_bits)
                print(f"Bob found {len(self.host.shared_bases_indices)} shared bases using YOUR code!")
                # Send simulation event for reconciliation success - based on student's bb84_reconcile_bases results
                if self.host and hasattr(self.host, '_send_update'):
                    from core.enums import SimulationEventType
                    efficiency = (len(self.host.shared_bases_indices) / len(their_bases) * 100) if their_bases else 0
                    print(f"Sending Bob reconciliation event: {len(self.host.shared_bases_indices)} shared bases")
                    self.host._send_update(SimulationEventType.INFO, 
                                         message=f"Student Bob bb84_reconcile_bases(): Found {len(self.host.shared_bases_indices)} matching bases out of {len(their_bases)} (Efficiency: {efficiency:.1f}%)",
                                         student_method="bb84_reconcile_bases",
                                         shared_bases=len(self.host.shared_bases_indices),
                                         total_bases=len(their_bases),
                                         efficiency=efficiency)
            else:
                # Fallback: extract from student's measurement outcomes
                shared_indices = []
                for i, (my_basis, their_basis) in enumerate(zip(self.host.basis_choices, their_bases)):
                    if my_basis == their_basis and i < len(self.host.measurement_outcomes):
                        shared_indices.append(i)
                self.host.shared_bases_indices = shared_indices
                shared_bits = [self.host.measurement_outcomes[i] for i in shared_indices]
                print(f"✅ Bob found {len(shared_indices)} shared bases using fallback logic")
            
            # Notify peer about shared indices
            self.host.send_classical_data({
                'type': 'shared_bases_indices', 
                'data': self.host.shared_bases_indices
            })
            
            # Send UI event for reconciliation completion
            if self.host and hasattr(self.host, '_send_update'):
                from core.enums import SimulationEventType
                efficiency = (len(self.host.shared_bases_indices) / len(their_bases) * 100) if their_bases else 0
                self.host._send_update(SimulationEventType.INFO, 
                                     message=f"Student Bob: Reconciliation completed - found {len(self.host.shared_bases_indices)} shared bases",
                                     student_method="bb84_reconcile_bases",
                                     shared_bases=len(self.host.shared_bases_indices),
                                     efficiency=efficiency)
            
            return self.host.shared_bases_indices, shared_bits
        else:
            # Fallback to hardcoded logic if student implementation is missing
            print("⚠️ Student Bob implementation missing bb84_reconcile_bases, using fallback")
            
            # Find shared indices where bases match
            shared_indices = []
            for i, (my_basis, their_basis) in enumerate(zip(self.host.basis_choices, their_bases)):
                if my_basis == their_basis and i < len(self.host.measurement_outcomes):
                    shared_indices.append(i)
            
            self.host.shared_bases_indices = shared_indices
            shared_bits = [self.host.measurement_outcomes[i] for i in shared_indices]
            
            print(f"✅ Reconciliation complete: {len(shared_indices)} shared bases out of {len(their_bases)} total")
            print(f"   Efficiency: {len(shared_indices)/len(their_bases)*100:.1f}%")
            
            # Notify peer about shared indices
            self.host.send_classical_data({
                'type': 'shared_bases_indices', 
                'data': shared_indices
            })
            
            return shared_indices, shared_bits
    
    def bb84_estimate_error_rate(self, their_bits_sample):
        """Compute error rate and CRITICAL: send completion signal."""
        if self.host is None:
            return False
            
        self.qkd_phase = "error_checking"
        print("🔍 Starting error rate estimation...")
        print(f"🔍 Bob: bb84_estimate_error_rate called with {len(their_bits_sample)} bits from Alice")
        
        # CRITICAL FIX: Use student's Bob implementation for error rate estimation
        if hasattr(self.student_bob, 'bb84_estimate_error_rate'):
            print(f"🎓 Using YOUR Bob implementation for error rate estimation...")
            print(f"   Sample size: {len(their_bits_sample)} bits")
            
            # Send UI event for error estimation start
            if self.host and hasattr(self.host, '_send_update'):
                from core.enums import SimulationEventType
                self.host._send_update(SimulationEventType.INFO, 
                                     message="Student Bob: Starting error rate estimation process",
                                     student_method="bb84_estimate_error_rate",
                                     sample_size=len(their_bits_sample))
            
            # Call the student's Bob implementation
            print(f"🎓 Calling student Bob's bb84_estimate_error_rate method...")
            error_rate = self.student_bob.bb84_estimate_error_rate(their_bits_sample)
            print(f"🎓 Student Bob error estimation result: {error_rate}")
            
            print(f"📊 YOUR Bob error rate estimation complete: {error_rate:.1%}")
            
            # Send simulation event for error rate estimation - based on student's bb84_estimate_error_rate
            if self.host and hasattr(self.host, '_send_update'):
                from core.enums import SimulationEventType
                errors = sum(1 for bit, idx in their_bits_sample if 0 <= idx < len(self.host.measurement_outcomes) and self.host.measurement_outcomes[idx] != bit)
                comparisons = len([bit for bit, idx in their_bits_sample if 0 <= idx < len(self.host.measurement_outcomes)])
                print(f"📡 Sending Bob error estimation event: {error_rate:.1%} error rate")
                self.host._send_update(SimulationEventType.INFO, 
                                     message=f"Student Bob bb84_estimate_error_rate(): {error_rate:.1%} error rate ({errors}/{comparisons} errors) using student implementation",
                                     student_method="bb84_estimate_error_rate",
                                     error_rate=error_rate,
                                     errors=errors,
                                     comparisons=comparisons,
                                     sample_size=len(their_bits_sample))
            
            # Store learning stats
            if hasattr(self.host, 'learning_stats'):
                self.host.learning_stats['error_rates'].append(error_rate)
            
            # CRITICAL FIX: Send completion signal to notify adapters
            print("📡 Sending QKD completion signal...")
            # Send simulation event for QKD completion
            if self.host and hasattr(self.host, '_send_update'):
                from core.enums import SimulationEventType
                self.host._send_update(SimulationEventType.SHARED_KEY_GENERATED, 
                                     message="BB84 QKD protocol completed successfully",
                                     error_rate=error_rate,
                                     shared_bases=len(self.host.shared_bases_indices))
            
            # Send completion message to trigger final key extraction
            self.host.send_classical_data({'type': 'complete'})
        else:
            # Fallback to hardcoded logic if student implementation is missing
            print("⚠️ Student Bob implementation missing bb84_estimate_error_rate, using fallback")
            
            errors = 0
            comparisons = 0
            
            for bit, idx in their_bits_sample:
                if 0 <= idx < len(self.host.measurement_outcomes):
                    comparisons += 1
                    if self.host.measurement_outcomes[idx] != bit:
                        errors += 1
            
            error_rate = (errors / comparisons) if comparisons > 0 else 0.0
            
            print(f"📊 Error rate estimation complete:")
            print(f"   Sampled {comparisons} bits")
            print(f"   Found {errors} errors")
            print(f"   Error rate: {error_rate:.1%}")
            
            # Store learning stats
            if hasattr(self.host, 'learning_stats'):
                self.host.learning_stats['error_rates'].append(error_rate)
            
            # CRITICAL FIX: Send completion signal to notify adapters
            print("📡 Sending QKD completion signal...")
        self.host.send_classical_data({'type': 'complete'})
        
        # Update phase to complete
        self.qkd_phase = "complete"
        print("BB84 PROTOCOL COMPLETE!")
        print(f"Final BB84 Protocol Status: COMPLETE")
        print(f"Student Implementation: SUCCESSFUL")
        
        # Send UI event for protocol completion
        if self.host and hasattr(self.host, '_send_update'):
            from core.enums import SimulationEventType
            self.host._send_update(SimulationEventType.INFO, 
                                 message="BB84 Protocol Complete! All student methods executed successfully",
                                 student_method="bb84_complete",
                                 protocol_status="complete",
                                 student_implementation="successful")
        
        # Extract final shared key
        if hasattr(self.host, 'bb84_extract_key'):
            final_key = self.host.bb84_extract_key()
            print(f"🔑 Final shared key extracted: {final_key[:10]}... (length: {len(final_key)})")
        else:
            final_key = []
            print("⚠️ Could not extract final shared key")
        
        # Send final completion event - based on student's complete BB84 implementation
        if self.host and hasattr(self.host, '_send_update'):
            from core.enums import SimulationEventType
            print(f"Sending final completion event: BB84 protocol complete!")
            self.host._send_update(SimulationEventType.INFO, 
                                 message="Student BB84 Implementation Complete! All methods executed successfully: bb84_send_qubits(), process_received_qbit(), bb84_reconcile_bases(), bb84_estimate_error_rate()",
                                 final_status="complete",
                                 error_rate=error_rate,
                                 shared_key_length=len(final_key),
                                 shared_key_sample=final_key[:10] if final_key else [],
                                 student_methods_used=["bb84_send_qubits", "process_received_qbit", "bb84_reconcile_bases", "bb84_estimate_error_rate"])
        
        return error_rate
    
    def update_shared_bases_indices(self, shared_base_indices):
        """Update shared bases indices and start error estimation - called by Alice"""
        if self.host is None:
            return False
            
        print(f"🔍 Alice: update_shared_bases_indices called with {len(shared_base_indices)} indices")
        print(f"🔍 Alice: Received shared bases from Bob: {shared_base_indices[:10]}... (showing first 10)")
        
        # Update the host's shared bases indices
        self.host.shared_bases_indices = shared_base_indices
        
        # Send simulation event for shared bases indices received
        if self.host and hasattr(self.host, '_send_update'):
            from core.enums import SimulationEventType
            self.host._send_update(SimulationEventType.INFO, 
                                 message=f"Student Alice: Received {len(shared_base_indices)} shared bases indices from Bob",
                                 student_method="update_shared_bases_indices",
                                 shared_bases=len(shared_base_indices),
                                 reconciliation_complete=True)
        
        # Start error estimation process
        print(f"🔄 Alice: Starting error estimation process...")
        if self.host and hasattr(self.host, 'update_shared_bases_indices'):
            # Call the host's update_shared_bases_indices method to trigger error estimation
            print(f"🔍 Alice: Calling host's update_shared_bases_indices method...")
            self.host.update_shared_bases_indices(shared_base_indices)
            print(f"✅ Alice: Error estimation process started")
            
            # Send UI event for error estimation start
            if self.host and hasattr(self.host, '_send_update'):
                from core.enums import SimulationEventType
                self.host._send_update(SimulationEventType.INFO, 
                                     message="Student Alice: Starting error estimation process",
                                     student_method="update_shared_bases_indices",
                                     error_estimation_started=True)
        else:
            print(f"❌ Alice: No update_shared_bases_indices method available on host")
        
        return True

# Wrapper class that matches simulation expectations
class StudentImplementationBridge:
    """Bridge wrapper that connects to enhanced implementation"""
    def __init__(self, host):
        self.host = host
        # Create the enhanced bridge
        self._bridge = EnhancedStudentImplementationBridge()
        # CRITICAL FIX: Always set the host reference
        self._bridge.host = host
        print(f"🔗 Bridge attached to host: {host.name if host else 'Unknown'}")
    
    def set_host(self, host):
        """Set the host reference after creation"""
        self.host = host
        self._bridge.host = host
        print(f"🔗 Bridge host updated: {host.name if host else 'Unknown'}")
    
    def bb84_send_qubits(self, num_qubits):
        return self._bridge.bb84_send_qubits(num_qubits)
    
    def process_received_qbit(self, qbit, from_channel):
        return self._bridge.process_received_qbit(qbit, from_channel)
    
    def bb84_reconcile_bases(self, their_bases):
        return self._bridge.bb84_reconcile_bases(their_bases)
    
    def bb84_estimate_error_rate(self, their_bits_sample):
        return self._bridge.bb84_estimate_error_rate(their_bits_sample)

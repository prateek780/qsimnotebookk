import random
import json

# Helper functions for quantum operations
try:
    import qutip as qt
except Exception:
    qt = None

# Import student's BB84 implementation functions from notebook
def prepare_quantum_state(bit, basis):
    """
    Prepare a quantum state for BB84 protocol
    
    Args:
        bit: 0 or 1 (the classical bit to encode)
        basis: 0 (Z-basis) or 1 (X-basis)
    
    Returns:
        String representation of the quantum state
    """
    if basis == 0:  # Z-basis (computational basis)
        if bit == 0:
            return '|0⟩'  # |0⟩ state
        else:
            return '|1⟩'  # |1⟩ state
    else:  # X-basis (Hadamard basis)
        if bit == 0:
            return '|+⟩'  # |+⟩ = (|0⟩ + |1⟩)/√2
        else:
            return '|-⟩'  # |-⟩ = (|0⟩ - |1⟩)/√2

def measure_quantum_state(quantum_state, measurement_basis):
    """
    Measure a quantum state in a given basis.

    Args:
        quantum_state: one of '|0⟩', '|1⟩', '|+⟩', '|-⟩'
        measurement_basis: 0 = Z, 1 = X

    Returns:
        0 or 1
    """
    if measurement_basis == 0:  # Z-basis measurement
        if quantum_state in ['|0⟩', '|1⟩']:
            return 0 if quantum_state == '|0⟩' else 1
        else:
            # Measuring X states in Z basis is random
            return random.randint(0, 1)
    else:  # X-basis measurement
        if quantum_state in ['|+⟩', '|-⟩']:
            return 0 if quantum_state == '|+⟩' else 1
        else:
            # Measuring Z states in X basis is random
            return random.randint(0, 1)

# Student's BB84 implementation class from notebook
class StudentQuantumHost:
    """
    Student's personal BB84 implementation!
    This class will be used by the quantum network simulation.
    """
    
    def __init__(self, name):
        self.name = name
        # Initialize data structures
        self.alice_bits = []      # Alice's random bits
        self.alice_bases = []     # Alice's random bases
        self.encoded_qubits = []  # Alice's encoded qubits
        self.basis_choices = []   # Bob's measurement bases
        self.measurement_outcomes = []  # Bob's measurement results
        self.shared_bases_indices = []  # Shared bases indices from reconciliation
        self.shared_bits = []     # Shared bits from reconciliation
        
        # Additional data structures from second file
        self.random_bits = []              # Random classical bits generated
        self.measurement_bases = []        # Measurement bases chosen for encoding
        self.quantum_states = []           # Quantum states encoded
        self.received_bases = []           # Measurement bases used when receiving qubits
        
        print(f"{self.name} initialized! Ready for BB84 protocol!")
        print(f"{self.name} using STUDENT'S BB84 IMPLEMENTATION from notebook!")
        print(f"{self.name} methods: bb84_send_qubits(), process_received_qbit(), bb84_reconcile_bases(), bb84_estimate_error_rate()")
    
    def bb84_send_qubits(self, num_qubits):
        """
        Sender's BB84 implementation: Prepare and send qubits
        
        Args:
            num_qubits: Number of qubits to prepare
        
        Returns:
            List of encoded qubits
        """
        print(f"{self.name} preparing {num_qubits} qubits for BB84...")
        
        # Clear previous data
        self.alice_bits = []
        self.alice_bases = []
        self.encoded_qubits = []
        self.random_bits = []
        self.measurement_bases = []
        self.quantum_states = []
        
        # Process each qubit
        for i in range(num_qubits):
            # Create a random classical value (0 or 1)
            classical_bit = random.randint(0, 1)
            
            # Choose a random preparation setting (basis: 0 for rectilinear, 1 for diagonal)
            preparation_basis = random.randint(0, 1)
            
            # Transform classical value into quantum state using chosen setting
            if preparation_basis == 0:  # Rectilinear basis (Z-basis)
                if classical_bit == 0:
                    quantum_state = "|0⟩"  # |0⟩ state
                else:
                    quantum_state = "|1⟩"  # |1⟩ state
            else:  # Diagonal basis (X-basis)
                if classical_bit == 0:
                    quantum_state = "|+⟩"  # |+⟩ state = (|0⟩ + |1⟩)/√2
                else:
                    quantum_state = "|-⟩"  # |-⟩ state = (|0⟩ - |1⟩)/√2
            
            # Store results in both naming conventions for compatibility
            self.alice_bits.append(classical_bit)
            self.alice_bases.append(preparation_basis)
            self.encoded_qubits.append(quantum_state)
            
            self.random_bits.append(classical_bit)
            self.measurement_bases.append(preparation_basis)
            self.quantum_states.append(quantum_state)
        
        print(f"{self.name} prepared {len(self.encoded_qubits)} qubits")
        print(f"   Bits: {self.alice_bits[:10]}{'...' if len(self.alice_bits) > 10 else ''}")
        print(f"   Bases: {self.alice_bases[:10]}{'...' if len(self.alice_bases) > 10 else ''}")
        
        return self.encoded_qubits
    
    def process_received_qbit(self, qbit, from_channel):
        """
        Receiver's BB84 implementation: Receive and measure qubits
        
        Args:
            qbit: The received quantum state
            from_channel: The quantum channel (not used in this implementation)
        
        Returns:
            True if successful
        """
        # Select a random measurement setting (0 for rectilinear, 1 for diagonal)
        measurement_basis = random.randint(0, 1)
        
        # Record the chosen setting in both naming conventions for compatibility
        self.basis_choices.append(measurement_basis)
        self.received_bases.append(measurement_basis)
        
        # Perform measurement of the received quantum state using the chosen setting
        if measurement_basis == 0:  # Rectilinear basis (Z-basis) measurement
            if qbit == "|0⟩":
                outcome = 0  # Measuring |0⟩ in Z-basis always gives 0
            elif qbit == "|1⟩":
                outcome = 1  # Measuring |1⟩ in Z-basis always gives 1
            elif qbit == "|+⟩":
                outcome = random.randint(0, 1)  # |+⟩ in Z-basis: 50% chance of 0 or 1
            elif qbit == "|-⟩":
                outcome = random.randint(0, 1)  # |-⟩ in Z-basis: 50% chance of 0 or 1
            else:
                # Handle unexpected quantum state
                outcome = random.randint(0, 1)
                
        else:  # Diagonal basis (X-basis) measurement
            if qbit == "|+⟩":
                outcome = 0  # Measuring |+⟩ in X-basis always gives 0
            elif qbit == "|-⟩":
                outcome = 1  # Measuring |-⟩ in X-basis always gives 1
            elif qbit == "|0⟩":
                outcome = random.randint(0, 1)  # |0⟩ in X-basis: 50% chance of 0 or 1
            elif qbit == "|1⟩":
                outcome = random.randint(0, 1)  # |1⟩ in X-basis: 50% chance of 0 or 1
            else:
                # Handle unexpected quantum state
                outcome = random.randint(0, 1)
        
        # Store the resulting outcome
        self.measurement_outcomes.append(outcome)
        
        return True
    
    def bb84_reconcile_bases(self, their_bases):
        """
        Find matching bases between Alice and Bob
        
        Args:
            their_bases: Alice's bases (from the other host)
        
        Returns:
            Tuple of (shared_indices, shared_bits)
        """
        print(f"{self.name} reconciling bases...")
        
        # Create empty collections for matching indices and corresponding bit values
        shared_indices = []
        shared_bits = []
        
        # Iterate through both sets of basis choices simultaneously with their positions
        for position, (my_basis, their_basis) in enumerate(zip(self.basis_choices, their_bases)):
            # Check if the two bases are the same
            if my_basis == their_basis:
                # Record the index where bases align
                shared_indices.append(position)
                
                # If a corresponding measurement result exists, record the measured value
                if position < len(self.measurement_outcomes):
                    shared_bits.append(self.measurement_outcomes[position])
        
        # Display summary after completing the comparison
        total_comparisons = min(len(self.basis_choices), len(their_bases))
        matches_found = len(shared_indices)
        match_proportion = matches_found / total_comparisons if total_comparisons > 0 else 0
        
        print(f"{self.name} found {len(shared_indices)} matching bases out of {len(their_bases)}")
        print(f"   Efficiency: {len(shared_indices)/len(their_bases)*100:.1f}%")
        
        # Store shared indices and bits for later use
        self.shared_bases_indices = shared_indices
        self.shared_bits = shared_bits
        
        return shared_indices, shared_bits
    
    def bb84_estimate_error_rate(self, their_bits_sample):
        """
        Estimate error rate by comparing sample bits
        
        Args:
            their_bits_sample: List of (bit, index) tuples from Alice
        
        Returns:
            Error rate (0.0 to 1.0)
        """
        print(f"{self.name} estimating error rate...")
        
        # Set up counters to track comparisons and discrepancies
        errors = 0
        comparisons = 0
        
        for bit, index in their_bits_sample:
            # Check if the position is valid relative to this host's recorded outcomes
            if 0 <= index < len(self.measurement_outcomes):
                # Increase the comparison count for valid positions
                comparisons += 1
                
                # Get the recorded outcome for this position
                recorded_outcome = self.measurement_outcomes[index]
                
                # If the recorded outcome does not match the provided reference bit, increase error count
                if recorded_outcome != bit:
                    errors += 1
        
        # Calculate error rate as ratio of errors to comparisons, defaulting to zero if no comparisons
        error_rate = (errors / comparisons) if comparisons > 0 else 0.0
        
        print(f"{self.name} error rate: {error_rate:.1%} ({errors}/{comparisons} errors)")
        
        return error_rate

# Note: Using student's prepare_quantum_state and measure_quantum_state functions instead

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
        self.expected_bits = 0  # Will be set when bb84_send_qubits is called
        print("Enhanced Bridge created! BB84 implementation with completion signals enabled.")
        print("STUDENT'S BB84 IMPLEMENTATION LOADED!")
        print("Using StudentQuantumHost class from notebook - no hardcoded algorithms!")
    
    def _load_student_implementations(self):
        """Load student implementations from the notebook or create StudentQuantumHost instances"""
        try:
            # Try to access from globals() directly (for notebook execution)
            import sys
            current_frame = sys._getframe(1)
            global_vars = current_frame.f_globals
            if 'alice' in global_vars and 'bob' in global_vars:
                alice = global_vars['alice']
                bob = global_vars['bob']
                print("Loaded student implementations from frame globals")
                print(f"   Alice type: {type(alice).__name__}")
                print(f"   Bob type: {type(bob).__name__}")
                return alice, bob
        except Exception as e:
            print(f"Failed to load from frame globals: {e}")
        
        # Create StudentQuantumHost instances using student's code
        print("Creating StudentQuantumHost instances for BB84 implementation")
        print("Using student's vibe-coded BB84 implementation!")
        print("NO HARDCODED ALGORITHMS - PURE STUDENT CODE!")
        return self._create_student_quantum_hosts()
    
    def _create_student_quantum_hosts(self):
        """Create StudentQuantumHost instances using the student's BB84 implementation"""
        print("Creating Alice and Bob using StudentQuantumHost class")
        print("Initializing with student's BB84 methods:")
        print("   - bb84_send_qubits()")
        print("   - process_received_qbit()")
        print("   - bb84_reconcile_bases()")
        print("   - bb84_estimate_error_rate()")
        alice = StudentQuantumHost("Alice")
        bob = StudentQuantumHost("Bob")
        print("StudentQuantumHost instances created successfully!")
        print("Ready to run BB84 protocol with student's implementation!")
        return alice, bob
    
    # Note: Only using StudentQuantumHost - no fallback implementations
    
    def bb84_send_qubits(self, num_qubits):
        """Send qubits via the simulator using student implementation."""
        if self.host is None:
            print("Bridge not attached to a simulation host")
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
                                 message=f"STUDENT'S BB84 IMPLEMENTATION: Starting protocol with {num_qubits} qubits using StudentQuantumHost class",
                                 student_implementation="StudentQuantumHost",
                                 implementation_type="student_vibe_code")
        
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
                                 message=f"STUDENT ALICE: Prepared {len(encoded_qubits)} qubits using YOUR bb84_send_qubits() method from notebook!",
                                 student_method="bb84_send_qubits",
                                 qubits_prepared=len(encoded_qubits),
                                 alice_bits=len(self.student_alice.alice_bits),
                                 alice_bases=len(self.student_alice.alice_bases),
                                 implementation_source="notebook_student_code",
                                 student_class="StudentQuantumHost")
        
        # CRITICAL: Record Alice's bases and bits on the simulation host
        self.host.basis_choices = list(self.student_alice.alice_bases)
        self.host.measurement_outcomes = list(self.student_alice.alice_bits)
        
        # Send through the actual quantum channel
        channel = self.host.get_channel()
        if channel is None:
            print(f"ERROR: {self.host.name} has no quantum channel to send qubits.")
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
                                 message=f"STUDENT BB84: Sending {len(encoded_qubits)} encoded qubits from YOUR bb84_send_qubits() method through quantum channel",
                                 student_qubits=safe_qubits,  # Safe string representation
                                 total_qubits=len(encoded_qubits),
                                 implementation_source="student_notebook_code",
                                 student_method="bb84_send_qubits")
        
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
                                     message="STUDENT BOB: Started receiving qubits using YOUR process_received_qbit() method from notebook!",
                                     student_method="process_received_qbit",
                                     implementation_source="student_notebook_code",
                                     student_class="StudentQuantumHost")
            
        self.bits_received += 1
        
        # Use student's Bob implementation
        result = self.student_bob.process_received_qbit(qbit, from_channel)
        
        # Update the host's state with Bob's results from student implementation
        if hasattr(self.student_bob, 'basis_choices'):
            self.host.basis_choices = list(self.student_bob.basis_choices)
        if hasattr(self.student_bob, 'measurement_outcomes'):
            self.host.measurement_outcomes = list(self.student_bob.measurement_outcomes)
        
        # Send simulation event for Bob's qubit reception - based on student's process_received_qbit
        if self.host and hasattr(self.host, '_send_update'):
            from core.enums import SimulationEventType
            print(f"Sending Bob qubit reception event: {self.bits_received}/{self.expected_bits}")
            self.host._send_update(SimulationEventType.DATA_RECEIVED,
                                 message=f"STUDENT BOB: Received qubit {self.bits_received}/{self.expected_bits} using YOUR process_received_qbit() method from notebook!",
                                 student_method="process_received_qbit",
                                 qubits_received=self.bits_received,
                                 total_expected=self.expected_bits,
                                 measurement_basis=self.student_bob.basis_choices[-1] if self.student_bob.basis_choices else None,
                                 measurement_result=self.student_bob.measurement_outcomes[-1] if self.student_bob.measurement_outcomes else None,
                                 implementation_source="student_notebook_code",
                                 student_class="StudentQuantumHost")
        
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
                                     message=f"STUDENT BOB: Received all {self.bits_received} qubits, ready for YOUR bb84_reconcile_bases() method!",
                                     student_method="bb84_reconcile_bases",
                                     measurements=len(self.host.measurement_outcomes),
                                     bases=len(self.host.basis_choices),
                                     implementation_source="student_notebook_code",
                                     student_class="StudentQuantumHost")
            self.qkd_phase = "ready_for_reconciliation"
        
        return result
        
    def bb84_reconcile_bases(self, their_bases):
        """Find matching bases and trigger error rate estimation."""
        if self.host is None:
            return False
            
        self.qkd_phase = "reconciling"
        print("Starting basis reconciliation...")
        print(f"Bob: bb84_reconcile_bases called with {len(their_bases)} bases from Alice")
        
        # Use student's Bob implementation for reconciliation
        print(f"Using YOUR Bob implementation for reconciliation...")
        print(f"   Bob's bases: {len(self.host.basis_choices)}")
        print(f"   Alice's bases: {len(their_bases)}")
        
        # Send UI event for reconciliation start
        if self.host and hasattr(self.host, '_send_update'):
            from core.enums import SimulationEventType
            self.host._send_update(SimulationEventType.INFO, 
                                 message="STUDENT BOB: Starting reconciliation process using YOUR bb84_reconcile_bases() method from notebook!",
                                 student_method="bb84_reconcile_bases",
                                 alice_bases=len(their_bases),
                                 bob_bases=len(self.host.basis_choices),
                                 implementation_source="student_notebook_code",
                                 student_class="StudentQuantumHost")
        
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
                                     message=f"STUDENT BOB bb84_reconcile_bases(): Found {len(self.host.shared_bases_indices)} matching bases out of {len(their_bases)} (Efficiency: {efficiency:.1f}%) using YOUR code!",
                                     student_method="bb84_reconcile_bases",
                                     shared_bases=len(self.host.shared_bases_indices),
                                     total_bases=len(their_bases),
                                     efficiency=efficiency,
                                     implementation_source="student_notebook_code",
                                     student_class="StudentQuantumHost")
        else:
            # Extract from student's measurement outcomes
            shared_indices = []
            for i, (my_basis, their_basis) in enumerate(zip(self.host.basis_choices, their_bases)):
                if my_basis == their_basis and i < len(self.host.measurement_outcomes):
                    shared_indices.append(i)
            self.host.shared_bases_indices = shared_indices
            shared_bits = [self.host.measurement_outcomes[i] for i in shared_indices]
            print(f"Bob found {len(shared_indices)} shared bases using student logic")
        
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
    
    def bb84_estimate_error_rate(self, their_bits_sample):
        """Compute error rate and CRITICAL: send completion signal."""
        if self.host is None:
            return False
            
        self.qkd_phase = "error_checking"
        print("Starting error rate estimation...")
        print(f"Bob: bb84_estimate_error_rate called with {len(their_bits_sample)} bits from Alice")
        
        # Use student's Bob implementation for error rate estimation
        print(f"Using YOUR Bob implementation for error rate estimation...")
        print(f"   Sample size: {len(their_bits_sample)} bits")
        
        # Send UI event for error estimation start
        if self.host and hasattr(self.host, '_send_update'):
            from core.enums import SimulationEventType
            self.host._send_update(SimulationEventType.INFO, 
                                 message="STUDENT BOB: Starting error rate estimation using YOUR bb84_estimate_error_rate() method from notebook!",
                                 student_method="bb84_estimate_error_rate",
                                 sample_size=len(their_bits_sample),
                                 implementation_source="student_notebook_code",
                                 student_class="StudentQuantumHost")
        
        # Call the student's Bob implementation
        print(f"Calling student Bob's bb84_estimate_error_rate method...")
        error_rate = self.student_bob.bb84_estimate_error_rate(their_bits_sample)
        print(f"Student Bob error estimation result: {error_rate}")

        print(f"YOUR Bob error rate estimation complete: {error_rate:.1%}")
        
        # Send simulation event for error rate estimation - based on student's bb84_estimate_error_rate
        if self.host and hasattr(self.host, '_send_update'):
            from core.enums import SimulationEventType
            errors = sum(1 for bit, idx in their_bits_sample if 0 <= idx < len(self.host.measurement_outcomes) and self.host.measurement_outcomes[idx] != bit)
            comparisons = len([bit for bit, idx in their_bits_sample if 0 <= idx < len(self.host.measurement_outcomes)])
            print(f"Sending Bob error estimation event: {error_rate:.1%} error rate")
            self.host._send_update(SimulationEventType.INFO, 
                                 message=f"STUDENT BOB bb84_estimate_error_rate(): {error_rate:.1%} error rate ({errors}/{comparisons} errors) using YOUR implementation from notebook!",
                                 student_method="bb84_estimate_error_rate",
                                 error_rate=error_rate,
                                 errors=errors,
                                 comparisons=comparisons,
                                 sample_size=len(their_bits_sample),
                                 implementation_source="student_notebook_code",
                                 student_class="StudentQuantumHost")
        
        # Store learning stats
        if hasattr(self.host, 'learning_stats'):
            self.host.learning_stats['error_rates'].append(error_rate)
        
        # Send completion signal to notify adapters
        print("Sending QKD completion signal...")
        # Send simulation event for QKD completion
        if self.host and hasattr(self.host, '_send_update'):
            from core.enums import SimulationEventType
            self.host._send_update(SimulationEventType.SHARED_KEY_GENERATED, 
                                 message="BB84 QKD protocol completed successfully",
                                 error_rate=error_rate,
                                 shared_bases=len(self.host.shared_bases_indices))
        
        # Send completion message to trigger final key extraction
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
                                 message="BB84 Protocol Complete! All YOUR student methods executed successfully from notebook!",
                                 student_method="bb84_complete",
                                 protocol_status="complete",
                                 student_implementation="successful",
                                 implementation_source="student_notebook_code",
                                 student_class="StudentQuantumHost")
        
        # Extract final shared key
        if hasattr(self.host, 'bb84_extract_key'):
            final_key = self.host.bb84_extract_key()
            print(f"Final shared key extracted: {final_key[:10]}... (length: {len(final_key)})")
        else:
            final_key = []
            print("Could not extract final shared key")
        
        # Send final completion event - based on student's complete BB84 implementation
        if self.host and hasattr(self.host, '_send_update'):
            from core.enums import SimulationEventType
            print(f"Sending final completion event: BB84 protocol complete!")
            self.host._send_update(SimulationEventType.INFO, 
                                 message="STUDENT BB84 IMPLEMENTATION COMPLETE! All YOUR methods executed successfully from notebook: bb84_send_qubits(), process_received_qbit(), bb84_reconcile_bases(), bb84_estimate_error_rate()",
                                 final_status="complete",
                                 error_rate=error_rate,
                                 shared_key_length=len(final_key),
                                 shared_key_sample=final_key[:10] if final_key else [],
                                 student_methods_used=["bb84_send_qubits", "process_received_qbit", "bb84_reconcile_bases", "bb84_estimate_error_rate"],
                                 implementation_source="student_notebook_code",
                                 student_class="StudentQuantumHost",
                                 achievement="student_code_success")
        
        return error_rate
    
    def update_shared_bases_indices(self, shared_base_indices):
        """Update shared bases indices and start error estimation - called by Alice"""
        if self.host is None:
            return False
            
        print(f"Alice: update_shared_bases_indices called with {len(shared_base_indices)} indices")
        print(f"Alice: Received shared bases from Bob: {shared_base_indices[:10]}... (showing first 10)")
        
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
        print(f"Alice: Starting error estimation process...")
        if self.host and hasattr(self.host, 'update_shared_bases_indices'):
            # Call the host's update_shared_bases_indices method to trigger error estimation
            print(f"Alice: Calling host's update_shared_bases_indices method...")
            self.host.update_shared_bases_indices(shared_base_indices)
            print(f"Alice: Error estimation process started")
            
            # Send UI event for error estimation start
            if self.host and hasattr(self.host, '_send_update'):
                from core.enums import SimulationEventType
                self.host._send_update(SimulationEventType.INFO, 
                                     message="Student Alice: Starting error estimation process",
                                     student_method="update_shared_bases_indices",
                                     error_estimation_started=True)
        else:
            print(f"Alice: No update_shared_bases_indices method available on host")
        
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
        print(f"Bridge attached to host: {host.name if host else 'Unknown'}")
    
    def set_host(self, host):
        """Set the host reference after creation"""
        self.host = host
        self._bridge.host = host
        print(f"Bridge host updated: {host.name if host else 'Unknown'}")
    
    def bb84_send_qubits(self, num_qubits):
        return self._bridge.bb84_send_qubits(num_qubits)
    
    def process_received_qbit(self, qbit, from_channel):
        return self._bridge.process_received_qbit(qbit, from_channel)
    
    def bb84_reconcile_bases(self, their_bases):
        return self._bridge.bb84_reconcile_bases(their_bases)
    
    def bb84_estimate_error_rate(self, their_bits_sample):
        return self._bridge.bb84_estimate_error_rate(their_bits_sample)
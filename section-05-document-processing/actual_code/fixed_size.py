def fixed_size_chunker(text, chunk_size, overlap):
  words = text.split()
  # List comprehension
  chunks = [" ".join(words[i: i + chunk_size]) for i in range(0, len(words), chunk_size - overlap)]
  return chunks

  # For loop
  chunks = []
  for i in range(0, len(words), chunk_size - overlap):
    chunk = words[i: i + chunk_size]
    chunks.append(" ".join(chunk)) 

  return chunks

  # Generator
  for i in range(0, len(words), chunk_size - overlap):
    chunk = words[i: i + chunk_size]
    yield " ".join(chunk)




sample_text = """

University Computing Acceptable Use Policy

The University of Edinburgh has adopted this Acceptable Use Policy to cover the use of all its computing and network facilities by staff, students and any other persons authorised to use them. This Policy supersedes all previous versions of the University Computing Regulations.

The Policy is available below in HTML format; and is also available as a PDF - University Computing Acceptable Use Policy 
Policy covering the acceptable use of Computing Facilities

Version 3 - May 2025
Introduction and Definitions

This Policy covers the acceptable use of all computing facilities administered on behalf of the University of Edinburgh (hereafter UoE). They will be reviewed periodically and amended as required. Any amended Policy will be published as a new edition; where no amendments are required, the current edition will be republished. The Policy will be (re)published in August of each year.

As well as this Policy, users must abide by other policies and/or codes as relevant, including internal UoE codes such as:

    the Code of Student Conduct;
    the relevant staff disciplinary policy;
    the University Data Protection Policy;
    the Dignity and Respect Policy, Trans Policy (Staff), Trans Policy (Students) and any related documents;
    the Information Security Policy;
    the Information Security BYOD Standard;
    the Protocol for Access to Data from the Corporate Student Record System;
    the Social Media Policy; and
    the Use of Operational Data Policy.

And external codes such as:

    the Acceptable Use Policy of the Joint Academic Network (JANET) available on the Web at Acceptable Use Policy | Jisc community;
    any terms of use or similar codes imposed by remote sites, where their computing facilities are accessed or used by UoE users; and
    any terms of use of similar codes imposed by any third party website or services accessed using UoE computing facilities, to the extent these do not conflict with any applicable internal UoE codes.

It is not the intention of UoE that this Policy should be used to unreasonably limit recognised academic freedoms.
In this Policy

"computing facilities" includes central [computing] services as provided by UoE Information Services Group and any [computing] service operated by or on behalf of UoE; UoE School or College or Professional Services; computers, IT hardware and services; personally owned computers and peripherals, and remote networks and services, when accessed from or via UoE computing facilities; and all programmable equipment; any associated software and data, including data created by persons other than users, and the networking elements which link computing facilities.

"users" include UoE staff, UoE students, and any other person authorised to use computing facilities

"Files" include data and software accessed via the computing facilities (but do not include manual files).

And words following the terms including, include, in particular or for example, or any similar phrase, shall be construed as illustrative and shall not limit the generality of the related general words.
Policy

1. Status of the Policy

Breach of this Policy by UoE staff or students is a disciplinary offence and may be dealt with under the appropriate disciplinary code or procedures. Where an offence has occurred, or is suspected to have occurred under UK or Scots law, the relevant user may also be reported to the police or other appropriate authority. The rules applicable to UoE’s investigation of breaches or suspected breaches are in clause 6 below.

 

2. Private use of computing facilities

Computing facilities are provided solely for use by staff in accordance with their normal duties of employment, and by students in connection with their university education. All other use, by any users, is private. Private use is allowed, as a privilege and not a right, but if abused or otherwise used in a way that interferes, either by timing or extent, with the availability of UoE computing facilities, will be treated as a breach of this Policy. Users should also note that, in the event of a breach of this Policy, their personal information may be deleted by UoE in accordance with clause 6. Any use which does not breach any other part of this Policy herein, but nonetheless brings UoE into disrepute, or breaches any other internal or external policies and/or codes with which a user is bound to comply from time to time, may also be treated as a breach of this Policy.

The computing facilities must not be used for inappropriate purposes in either a private or other capacity. Inappropriate use of computing facilities includes, but is not limited to:

    use which is unlawful or fraudulent or has any unlawful or fraudulent purpose or effect.
    use for the purpose of harming or attempting to harm minors in any way;
    use to bully, insult, intimidate or humiliate any person, or the creation or transmission of material with the intent to cause annoyance, inconvenience or needless anxiety;
    use to transmit, or procure the sending of, any unsolicited or unauthorised advertising or promotional material or any other form of similar solicitation (spam);
    use to knowingly transmit any data, send or upload any material that contains viruses, Trojan horses, worms, time-bombs, keystroke loggers, spyware, adware or any other harmful programs or similar computer code designed to adversely affect the operation of any computer software or hardware;
    viewing, creation or transmission, or causing the transmission, of any offensive, obscene or indecent images, data or other material, or any data capable of being resolved into obscene, pornographic or indecent images or material;
    creation or transmission of defamatory material;
    creation or transmission of material such that this infringes the copyright of another person;
    deliberate unauthorised access to networked facilities or services;
    corrupting or destroying other users’ data;
    violating the privacy of other users;
    disrupting the work of other users; or
    denying or affecting the availability or performance of services to other users.

 

3. Damage to computing facilities
No person shall, unless appropriately authorised, take any action which damages, restricts, or undermines the performance, usability or accessibility of computing facilities; "taking action" may include deliberate omission or neglect, where action might reasonably have been expected as part of a user's duties.
 
 
4. By-passing Security Controls
No person shall, unless appropriately authorised, take any deliberate action with the intent to by-pass or circumvent any security controls installed to protect University digital systems or services. "Take action" includes attempts or successful implementation of unauthorised changes and includes acts or omissions.  
 
5. Compliance with law

Users must comply with the provisions of all current applicable UK or Scots law, including:

    intellectual property law, including laws concerning copyright, trademarks, and patents;
    the Computer Misuse Act 1990, and associated instruments;
    anti-harassment, hate crime and defamation laws, including the Protection from Harassment Act 1997, the Crime and Disorder Act 1998, the Defamation and Malicious Publication (Scotland) Act 2021, and the Hate Crime and Public Order (Scorland) Act 2021;
    data protection laws; including the Data Protection Act 2018 and UK GDPR;
    Freedom of Information laws;
    the interception and monitoring laws under the Regulation of Investigatory Powers Act 2000 (RIPA 2000); and
    the Terrorism Act 2000, the Terrorism Act 2006 and the Counter­Terrorism and Security Act (2015)

Under the Lawful Business Regulations (LBR), the UoE draws to the attention of all users the fact that their communications may be intercepted where lawful under RIPA 2000. The full UoE notice can be found at Statutory Notices | The University of Edinburgh

The UoE also draws to the attention of all users to its statutory obligation under the Counter-Terrorism and Security Act (2015) and under the Prevent Duty to have due regard to the need to prevent people being drawn into terrorism. The full UoE notice can be found at Prevent Duty | The University of Edinburgh

The Terrorism Act (2000) defines terrorism in section 1 of the Act, see Terrorism Act (2000) section 1 information

Users must also comply with the terms of any licence agreement or terms and conditions between the UoE and a third party which governs the use or installation of hardware, software or access to data when such use or access is facilitated by the computing facilities, to the extent those terms do not conflict with this Policy.

If users are accessing a service via UoE computing facilities that is hosted in a foreign jurisdiction, they may also be subject to local laws which apply to that service. In these case, particular care should be taken to comply with any relevant terms applicable to that service.

 

6. Security, confidentiality and passwords

Users must take all reasonable care to maintain the security of computing facilities and information to which they have been given approved access. In particular, users must not transfer or share their passwords, access tokens (in whatever format), IT credentials or rights to access or use computing facilities, to or with anyone else. Similarly, IT credentials granting access to University systems must not be shared or reused with any external service and users must not attempt to obtain or use anyone else’s credentials.

The confidentiality, integrity and security of all personally identifying data held, or processed on UoE systems must be respected, even where users have been authorised to access it.

Users must ensure that all portable devices used to access UoE information are protected by encryption, whether the device was purchased by the University, is personally owned or belongs to a third party.[1]

Users must not transfer any data outwith the University via the use of ‘auto­forward’ email rules to personal emails accounts unless they have been granted explicit permission to do so.

Guidance on how to encrypt portable devices can be found at Encrypting devices and documents | Information Security

Prior to terminating their relationship with the UoE, users must make appropriate arrangements for the secure return of all UoE computer equipment and for the secure destruction of UoE data in their possession, unless alternative arrangements are agreed beforehand with their line manager and approved by Head of School/Support Unit

Users must ensure the secure destruction of all UoE data prior to disposing of computer equipment, including personally owned devices. These requirements also apply if any equipment is being sent for repair or upgrade as these actions could allow unauthorised third parties to access UoE information. If users are unsure of how to undertake this requirement, they must contact their IT support team for advice prior to disposal or repair of the computer equipment.

Passwords used to access UoE systems or data must not be used to access non-UoE services, including commercial services such as Facebook, Google, social communication and networking apps, Amazon, personal emails etc. Additionally, where possible, the same limitation should apply to usernames used in the UoE, whether centrally generated or created by individual users.

[1] Please note that iPhones and iPads are automatically encrypted if you set a password. Android has an easy option in settings to encrypt the device.

 

7. Investigation of breaches

If the UoE suspects any breach or potential breach of the Policy by any user, it shall have full and unrestricted power to access all relevant computing facilities and files (including mobile devices and privately owned devices used to access UoE services, including UoE email) and to take all steps which it may deem reasonable to remove or prevent distribution of any UoE material. It may also require that any encrypted data is made available in human-readable form. UoE may also immediately suspend a user's access to computing facilities and, where appropriate, examine such user’s mobile device(s) for UoE material and remove any such material pending an investigation by an Authorised Officer or nominee of UoE as defined in the relevant Disciplinary Policy or Code of Conduct where the user is a UoE staff member or student respectively. Although we do not intend to wipe other data that is personal in nature (such as photographs or personal files or e-mails), it may not be possible to distinguish all such information from UoE material in all circumstances. In particular, where a user’s personal data is contained alongside UoE data (for example, if a personal email is sent or received using UoE’s email system), it will not be possible to distinguish this from UoE data and such personal data may be wiped. For this reason, you are encouraged not to use UoE email for personal purposes and, if you do, to mark any personal emails “personal” in the subject header. Similarly, you should not use personal email accounts for University business. Users who use mobile devices for UoE related activity should also regularly backup any personal data contained on their device(s).

 

8. Liability

By using the computing facilities each user agrees that the UoE shall (to the maximum extent permitted by law) have no liability for any:

    loss of, or corruption or damage to, any files or data contained therein; or
    loss or damage (including any special, indirect or consequential loss) to users or to third parties, or their equipment, operating systems or other assets

resulting from the use of UoE computing facilities, or any withdrawal of the use of said facilities at any time by UoE.

Users also agree that UoE is not liable for any consequences arising from the unavailability of the UoE computing facilities and related services, no matter how caused.

Each user agrees that UoE has the right to take legal action against individuals who cause it to suffer loss or damage (including damage to its reputation) as a result of that user's breach of this Policy, and to seek reimbursement of such loss, and/or any associated costs (including the costs of legal proceedings) arising from such a breach.

 

If you require this document in an alternative format, please contact Claire Maguire on 0131 650 4976 or email Claire.Maguire@ed.ac.uk

 

As well as this Policy, users must abide by other relevant policies or codes, including internal University policies such as those listed below.
"""

for chunk in fixed_size_chunker(sample_text, 200, 50):
  print(f"Chunk: {chunk}")


def analyze_chunk_quality(chunks):
    """
    Analyze the quality of fixed-size chunks.
    
    This implements the quality assessment metrics from the slides.
    
    Args:
        chunks: List of DocumentChunk objects
        
    Returns:
        Dictionary with quality metrics
    """
    if not chunks:
        return {"error": "No chunks to analyze"}
    
    word_counts = [c.word_count for c in chunks]
    
    # Calculate statistics
    avg_words = sum(word_counts) / len(word_counts)
    min_words = min(word_counts)
    max_words = max(word_counts)
    
    # Count problematic chunks
    very_short = sum(1 for wc in word_counts if wc < 50)
    very_long = sum(1 for wc in word_counts if wc > 1000)
    
    # Check for broken sentences (chunks ending mid-sentence)
    broken_sentences = 0
    for chunk in chunks:
        text = chunk.text.strip()
        if text and not text.endswith(('.', '!', '?', ':', ';')):
            broken_sentences += 1
    
    # Calculate quality score (0-100)
    quality_score = 100
    quality_score -= (very_short / len(chunks)) * 30  # Penalty for very short chunks
    quality_score -= (very_long / len(chunks)) * 20   # Penalty for very long chunks
    quality_score -= (broken_sentences / len(chunks)) * 50  # Penalty for broken sentences
    
    return {
        "total_chunks": len(chunks),
        "avg_words_per_chunk": round(avg_words, 1),
        "min_words": min_words,
        "max_words": max_words,
        "very_short_chunks": very_short,
        "very_long_chunks": very_long,
        "broken_sentences": broken_sentences,
        "quality_score": max(0, round(quality_score, 1))
    }
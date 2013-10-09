<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

  <xsl:template match="*">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="text()">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="step[11]">
    <xsl:param name="id">
      <xsl:choose>
        <xsl:when test="parent::procedure[@id]">
          <xsl:value-of select="parent::procedure/@id"/>
        </xsl:when>
        <xsl:when test="parent::procedure/title">
          "<xsl:value-of select="title"/>"
        </xsl:when>
        <xsl:otherwise>
          "<xsl:value-of select="substring(step[1]/text(), 1, 50)"/>..."
        </xsl:otherwise>
      </xsl:choose>
    </xsl:param>
    <xsl:param name="number-steps">
      <xsl:apply-templates select="parent::procedure/step[last()]" mode="count"/>
    </xsl:param>

    <xsl:message>(!) Procedure <xsl:value-of select="$id"/> has <xsl:value-of select="$number-steps"/> steps.
    Procedures may contain up to 10 steps.</xsl:message>
  </xsl:template>

  <xsl:template match="step" mode="count">
    <xsl:number select="step"/>
  </xsl:template>

</xsl:stylesheet>